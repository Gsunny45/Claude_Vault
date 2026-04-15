#!/usr/bin/env python3
"""
Task Router — reads tasks from Claude Vault, routes them to execution agents,
tracks state transitions, and logs everything.

Flow:  Task (vault markdown) → Router → Agent (subprocess/API) → Execution → Log

This is the control-plane dispatcher. It does NOT execute tasks itself.
It reads task files, determines routing, invokes agents, and records results.

Usage:
    python task_router.py scan                          # list routable tasks
    python task_router.py route TSK-0001                # route a specific task
    python task_router.py route --auto                  # auto-route all open tasks by priority
    python task_router.py agents                        # list registered agents
    python task_router.py status                        # pipeline status from monitor state

Agent registration is in _system/vault_config.yaml (or inline defaults).
Execution is via subprocess (Python scripts, CLI tools) — no cloud API calls from here.

Deps: stdlib only. ~10 MB RSS.
"""

import os
import re
import json
import subprocess
import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# ─── Configuration ──────────────────────────────────────────────

CLAUDE_VAULT = Path(os.environ.get(
    "CLAUDE_VAULT",
    r"C:\Users\MarsBase\Documents\Claude_Vault"
))

TASKS_DIR = "tasks"
ROUTING_LOG = "_system/logs/task_routing.jsonl"

# Agent definitions — extend via config or CLI
# Each agent has: name, type (script|command|api), path/command, capabilities (list of task tags)
DEFAULT_AGENTS = [
    {
        "name": "vault_bridge",
        "type": "script",
        "path": "_system/vault_bridge.py",
        "capabilities": ["sync", "cross-vault", "bridge"],
        "description": "Cross-vault state sync between Claude Vault and Local-Network-Hub",
    },
    {
        "name": "vault_monitor",
        "type": "script",
        "path": "_system/vault_monitor.py",
        "args": ["--once"],
        "capabilities": ["monitor", "scan", "health"],
        "description": "Filesystem change detection and vault health snapshots",
    },
    {
        "name": "vault_exporter",
        "type": "script",
        "path": "_system/vault_exporter.py",
        "capabilities": ["metrics", "prometheus", "monitoring"],
        "description": "Prometheus metrics exporter for vault health",
    },
    {
        "name": "llm_router",
        "type": "script",
        "path": "llm-orchestrator/backend/main.py",
        "capabilities": ["llm", "generation", "analysis", "code", "writing"],
        "description": "LLM orchestrator — routes to cheapest/free provider",
    },
    {
        "name": "manual",
        "type": "manual",
        "path": None,
        "capabilities": ["*"],
        "description": "Human or external agent — task flagged for manual pickup",
    },
]


# ─── Logging ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("task_router")


# ─── Frontmatter Parser ────────────────────────────────────────

def parse_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter as a flat dict."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(8192)
    except (OSError, IOError):
        return {}
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).splitlines():
        kv = re.match(r"^(\w[\w_-]*)\s*:\s*(.+)$", line)
        if kv:
            fm[kv.group(1).strip()] = kv.group(2).strip().strip('"').strip("'")
    return fm


def read_task_body(filepath: Path) -> str:
    """Read the markdown body (after frontmatter)."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (OSError, IOError):
        return ""
    match = re.match(r"^---\s*\n.*?\n---\s*\n?(.*)", content, re.DOTALL)
    return match.group(1).strip() if match else content.strip()


# ─── Task Scanner ───────────────────────────────────────────────

class Task:
    """Parsed task from vault."""
    def __init__(self, path: Path, fm: dict, body: str):
        self.path = path
        self.id = fm.get("id", path.stem)
        self.title = fm.get("title", "Untitled")
        self.status = fm.get("status", "unknown")
        self.created = fm.get("created", "")
        self.priority = fm.get("priority", "medium")
        self.tags = [t.strip() for t in fm.get("tags", "").split(",") if t.strip()]
        self.depends_on = fm.get("depends_on", "")
        self.assigned_agent = fm.get("assigned_agent", "")
        self.assigned_session = fm.get("assigned_session", "")
        self.body = body
        self.fm = fm

    @property
    def is_routable(self) -> bool:
        """Task can be routed if open and not blocked."""
        return self.status in ("open", "ready")

    @property
    def is_blocked(self) -> bool:
        return self.status == "blocked" or bool(self.depends_on and self.depends_on != "[]")

    @property
    def priority_score(self) -> int:
        """Numeric priority for sorting (lower = higher priority)."""
        return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(self.priority, 2)

    def __repr__(self):
        return f"<Task {self.id} [{self.status}] {self.title}>"


def scan_tasks(vault: Path) -> list[Task]:
    """Scan tasks/ folder and return parsed Task objects."""
    tasks_dir = vault / TASKS_DIR
    if not tasks_dir.exists():
        return []

    tasks = []
    for md in sorted(tasks_dir.glob("TSK-*.md")):
        fm = parse_frontmatter(md)
        body = read_task_body(md)
        tasks.append(Task(md, fm, body))
    return tasks


# ─── Agent Matcher ──────────────────────────────────────────────

def match_agent(task: Task, agents: list[dict]) -> Optional[dict]:
    """
    Pick the best agent for a task based on:
    1. Explicit assignment (task frontmatter has assigned_agent)
    2. Tag matching (task tags vs agent capabilities)
    3. Body keyword heuristic
    4. Fallback to manual
    """
    # Explicit assignment
    if task.assigned_agent:
        for a in agents:
            if a["name"] == task.assigned_agent:
                return a

    # Tag matching
    body_lower = task.body.lower()
    title_lower = task.title.lower()
    search_text = f"{' '.join(task.tags)} {title_lower} {body_lower}"

    best_agent = None
    best_score = 0

    for a in agents:
        if a["type"] == "manual":
            continue  # manual is fallback only
        score = 0
        for cap in a["capabilities"]:
            if cap in search_text:
                score += 1
        if score > best_score:
            best_score = score
            best_agent = a

    if best_agent and best_score > 0:
        return best_agent

    # Fallback to manual
    for a in agents:
        if a["name"] == "manual":
            return a
    return None


# ─── Execution Engine ───────────────────────────────────────────

def execute_agent(agent: dict, task: Task, vault: Path, dry_run: bool = False) -> dict:
    """
    Invoke an agent for a task. Returns execution result dict.
    In dry_run mode, just returns what would happen.
    """
    result = {
        "task_id": task.id,
        "agent": agent["name"],
        "agent_type": agent["type"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
    }

    if dry_run:
        result["status"] = "dry_run"
        result["message"] = f"Would route {task.id} to {agent['name']}"
        return result

    if agent["type"] == "manual":
        result["status"] = "queued_manual"
        result["message"] = f"Task {task.id} flagged for manual pickup"
        return result

    if agent["type"] == "script":
        script_path = vault / agent["path"]
        if not script_path.exists():
            result["status"] = "error"
            result["message"] = f"Agent script not found: {agent['path']}"
            return result

        cmd = [sys.executable, str(script_path)]
        extra_args = agent.get("args", [])
        if extra_args:
            cmd.extend(extra_args)
        # Pass vault path
        cmd.extend(["--vault", str(vault)])

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120,
                cwd=str(vault)
            )
            result["status"] = "success" if proc.returncode == 0 else "error"
            result["returncode"] = proc.returncode
            result["stdout"] = proc.stdout[-2000:] if proc.stdout else ""
            result["stderr"] = proc.stderr[-1000:] if proc.stderr else ""
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["message"] = "Agent timed out after 120s"
        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)

        return result

    if agent["type"] == "command":
        # Future: arbitrary shell command execution
        result["status"] = "not_implemented"
        result["message"] = "Command-type agents not yet implemented"
        return result

    result["status"] = "unknown_type"
    return result


# ─── Event Logging ──────────────────────────────────────────────

def log_routing_event(vault: Path, event: dict):
    """Append routing event to JSONL log."""
    log_path = vault / ROUTING_LOG
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, default=str) + "\n")


# ─── CLI Commands ───────────────────────────────────────────────

def cmd_scan(vault: Path):
    """List all tasks and their routing status."""
    tasks = scan_tasks(vault)
    agents = DEFAULT_AGENTS

    print(f"\n{'ID':<12} {'Status':<14} {'Pri':<8} {'Agent Match':<20} Title")
    print("-" * 90)
    for t in tasks:
        agent = match_agent(t, agents)
        agent_name = agent["name"] if agent else "none"
        marker = "→" if t.is_routable else "×" if t.is_blocked else " "
        print(f"{marker} {t.id:<10} {t.status:<14} {t.priority:<8} {agent_name:<20} {t.title[:40]}")

    routable = [t for t in tasks if t.is_routable]
    print(f"\n{len(tasks)} total, {len(routable)} routable")


def cmd_route(vault: Path, task_id: Optional[str], auto: bool, dry_run: bool):
    """Route one or more tasks to agents."""
    tasks = scan_tasks(vault)
    agents = DEFAULT_AGENTS

    if auto:
        targets = sorted(
            [t for t in tasks if t.is_routable],
            key=lambda t: t.priority_score
        )
        if not targets:
            print("No routable tasks found.")
            return
    elif task_id:
        targets = [t for t in tasks if t.id == task_id]
        if not targets:
            print(f"Task {task_id} not found.")
            return
    else:
        print("Specify a task ID or use --auto")
        return

    for task in targets:
        agent = match_agent(task, agents)
        if not agent:
            log.warning(f"No agent match for {task.id}")
            continue

        log.info(f"ROUTE  {task.id} → {agent['name']}  "
                 f"[{task.priority}] {task.title[:50]}")

        result = execute_agent(agent, task, vault, dry_run=dry_run)
        log_routing_event(vault, result)

        status_icon = {"success": "✓", "dry_run": "~", "queued_manual": "⏳",
                       "error": "✗", "timeout": "⏱"}.get(result["status"], "?")
        print(f"  {status_icon} {task.id} → {agent['name']}: {result['status']}")

        if result.get("stdout"):
            # Print first few lines of output
            lines = result["stdout"].strip().splitlines()[:5]
            for line in lines:
                print(f"    │ {line}")

        if result.get("stderr") and result["status"] == "error":
            print(f"    ⚠ {result['stderr'][:200]}")


def cmd_agents(vault: Path):
    """List registered agents."""
    agents = DEFAULT_AGENTS
    print(f"\n{'Name':<20} {'Type':<10} {'Capabilities':<35} Description")
    print("-" * 90)
    for a in agents:
        caps = ", ".join(a["capabilities"][:4])
        print(f"{a['name']:<20} {a['type']:<10} {caps:<35} {a['description'][:35]}")


def cmd_status(vault: Path):
    """Show pipeline status from monitor state + routing log."""
    # Read monitor state
    monitor_state = vault / "_system" / "_monitor_state.json"
    if monitor_state.exists():
        with open(monitor_state, "r") as f:
            state = json.load(f)
        print(f"\nVault Monitor State ({state.get('timestamp', '?')})")
        print(f"  Files tracked: {state.get('total_files', '?')}")
        by_status = state.get("by_status", {})
        for s, count in sorted(by_status.items()):
            print(f"    {s}: {count}")
    else:
        print("\nNo monitor state found. Run vault_monitor.py --once first.")

    # Read token state
    token_state = vault / "_system" / "_token_state.json"
    if token_state.exists():
        with open(token_state, "r") as f:
            ts = json.load(f)
        totals = ts.get("totals", {})
        print(f"\nToken Usage (last {ts.get('period_days', '?')} day(s))")
        print(f"  Requests: {totals.get('request_count', 0)}")
        print(f"  Tokens:   {totals.get('total_tokens', 0):,}")
        print(f"  Cost:     ${totals.get('total_cost', 0):.4f}")

    # Read recent routing events
    routing_log = vault / ROUTING_LOG
    if routing_log.exists():
        with open(routing_log, "r") as f:
            lines = f.readlines()
        recent = lines[-10:]
        print(f"\nRecent Routing Events ({len(lines)} total)")
        for line in recent:
            try:
                ev = json.loads(line.strip())
                print(f"  [{ev.get('timestamp', '?')[:19]}] "
                      f"{ev.get('task_id', '?')} → {ev.get('agent', '?')}: "
                      f"{ev.get('status', '?')}")
            except json.JSONDecodeError:
                continue
    else:
        print("\nNo routing events yet.")


# ─── Main ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Task Router — route vault tasks to execution agents"
    )
    parser.add_argument("--vault", type=str, default=str(CLAUDE_VAULT))
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("scan", help="List tasks and routing matches")
    sub.add_parser("agents", help="List registered agents")
    sub.add_parser("status", help="Pipeline status overview")

    route_cmd = sub.add_parser("route", help="Route task(s) to agents")
    route_cmd.add_argument("task_id", nargs="?", help="Task ID (e.g., TSK-0001)")
    route_cmd.add_argument("--auto", action="store_true", help="Auto-route all open tasks")
    route_cmd.add_argument("--dry-run", action="store_true", help="Show routing without executing")

    args = parser.parse_args()
    vault = Path(args.vault)

    if args.command == "scan":
        cmd_scan(vault)
    elif args.command == "route":
        cmd_route(vault, getattr(args, "task_id", None),
                  getattr(args, "auto", False),
                  getattr(args, "dry_run", False))
    elif args.command == "agents":
        cmd_agents(vault)
    elif args.command == "status":
        cmd_status(vault)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
