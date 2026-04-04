#!/usr/bin/env python3
"""
Vault Bridge — syncs state between Claude Vault and Local-Network-Hub.

Runs periodically or on-demand. Reads from both vaults and maintains
cross-references so each vault knows about the other's state.

Usage:
    python vault_bridge.py              # Run once
    python vault_bridge.py --watch 120  # Run every 120 seconds
"""

import os
import re
import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ──────────────────────────────────────────────
CLAUDE_VAULT = Path(os.environ.get(
    "CLAUDE_VAULT",
    r"C:\Users\MarsBase\Documents\Claude_Vault"
))
HUB_VAULT = Path(os.environ.get(
    "HUB_VAULT",
    r"C:\Users\MarsBase\Documents\Local-Network-Hub"
))

# ─── Frontmatter Parser ────────────────────────────────────────
def parse_frontmatter(filepath):
    """Extract YAML frontmatter as a dict from a markdown file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(8192)  # only need the top
    except (OSError, IOError):
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    fm = {}
    for line in match.group(1).splitlines():
        # Simple key: value parsing (handles strings, lists skipped)
        kv = re.match(r"^(\w[\w_-]*)\s*:\s*(.+)$", line)
        if kv:
            key = kv.group(1).strip()
            val = kv.group(2).strip().strip('"').strip("'")
            fm[key] = val
    return fm


def scan_vault_notes(vault_path, folders=None):
    """Scan a vault and return list of (relative_path, frontmatter_dict, mtime)."""
    notes = []
    vault = Path(vault_path)
    if not vault.exists():
        return notes

    for md in vault.rglob("*.md"):
        rel = md.relative_to(vault).as_posix()
        # Skip hidden dirs and templates
        if rel.startswith(".") or rel.startswith("_templates"):
            continue
        if folders and not any(rel.startswith(f) for f in folders):
            continue
        fm = parse_frontmatter(md)
        mtime = md.stat().st_mtime
        notes.append((rel, fm, mtime))
    return notes


# ─── Bridge Actions ─────────────────────────────────────────────

def sync_handoff_to_briefing():
    """
    Read Local-Network-Hub's _handoff.md and surface key state
    into Claude Vault's knowledge as a cross-reference.
    """
    handoff_path = HUB_VAULT / "_handoff.md"
    if not handoff_path.exists():
        return None

    fm = parse_frontmatter(handoff_path)
    with open(handoff_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Extract key sections
    sections = {}
    current = None
    for line in content.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current:
            sections[current].append(line)

    return {
        "frontmatter": fm,
        "sections": {k: "\n".join(v).strip() for k, v in sections.items()},
        "mtime": handoff_path.stat().st_mtime,
    }


def sync_hub_projects():
    """Read active projects from Local-Network-Hub."""
    projects = []
    proj_dir = HUB_VAULT / "01-Projects"
    if not proj_dir.exists():
        return projects

    for md in proj_dir.glob("*.md"):
        fm = parse_frontmatter(md)
        if fm.get("status") in ("active", "paused"):
            projects.append({
                "name": md.stem,
                "status": fm.get("status", "unknown"),
                "priority": fm.get("priority", "medium"),
                "updated": fm.get("updated", "unknown"),
            })
    return projects


def sync_hub_sessions():
    """Read recent sessions from Local-Network-Hub."""
    sessions = []
    sess_dir = HUB_VAULT / "00-System" / "Sessions"
    if not sess_dir.exists():
        return sessions

    for md in sorted(sess_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
        fm = parse_frontmatter(md)
        sessions.append({
            "name": md.stem,
            "agent": fm.get("agent", "unknown"),
            "status": fm.get("status", "unknown"),
            "project": fm.get("project", ""),
            "created": fm.get("created", "unknown"),
        })
    return sessions


def write_bridge_report():
    """Write a cross-vault state report into Claude Vault."""
    now = datetime.now(timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    now_date = now.strftime("%Y-%m-%d")

    # Gather data
    handoff = sync_handoff_to_briefing()
    projects = sync_hub_projects()
    hub_sessions = sync_hub_sessions()

    # Count Claude Vault state
    cv_tasks = scan_vault_notes(CLAUDE_VAULT, ["tasks/"])
    cv_decisions = scan_vault_notes(CLAUDE_VAULT, ["decisions/"])
    cv_knowledge = scan_vault_notes(CLAUDE_VAULT, ["knowledge/"])

    open_tasks = [n for n in cv_tasks if n[1].get("status") in ("open", "in_progress")]
    accepted_decisions = [n for n in cv_decisions if n[1].get("status") == "accepted"]
    stale_knowledge = [n for n in cv_knowledge if n[1].get("confidence") == "stale"]

    # Build report
    lines = [
        "---",
        "type: bridge_report",
        f"compiled: \"{now_iso}\"",
        f"claude_vault_tasks_open: {len(open_tasks)}",
        f"claude_vault_decisions_accepted: {len(accepted_decisions)}",
        f"claude_vault_knowledge_stale: {len(stale_knowledge)}",
        f"hub_projects_active: {len([p for p in projects if p['status'] == 'active'])}",
        f"hub_sessions_recent: {len(hub_sessions)}",
        "---",
        "",
        f"# Vault Bridge Report — {now_date}",
        "",
        "## Claude Vault State",
        f"- **Open tasks:** {len(open_tasks)}",
        f"- **Accepted decisions:** {len(accepted_decisions)}",
        f"- **Stale knowledge:** {len(stale_knowledge)}",
        f"- **Total knowledge entries:** {len(cv_knowledge)}",
        "",
    ]

    if open_tasks:
        lines.append("### Open Tasks")
        for path, fm, _ in open_tasks:
            lines.append(f"- [[{path}|{fm.get('title', path)}]] ({fm.get('status', '?')})")
        lines.append("")

    lines.append("## Local-Network-Hub State")
    lines.append("")

    if handoff:
        handoff_date = datetime.fromtimestamp(handoff["mtime"]).strftime("%Y-%m-%d %H:%M")
        lines.append(f"**Last handoff:** {handoff_date}")
        lines.append("")
        for section_name, section_body in handoff["sections"].items():
            if section_body.strip():
                lines.append(f"### {section_name}")
                lines.append(section_body[:500])  # cap length
                lines.append("")
    else:
        lines.append("*No _handoff.md found in Local-Network-Hub.*")
        lines.append("")

    if projects:
        lines.append("### Active Projects")
        for p in projects:
            lines.append(f"- **{p['name']}** — {p['status']} (priority: {p['priority']}, updated: {p['updated']})")
        lines.append("")

    if hub_sessions:
        lines.append("### Recent Hub Sessions")
        for s in hub_sessions:
            lines.append(f"- **{s['name']}** — {s['agent']} ({s['status']})")
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated by vault_bridge.py at {now_iso}*")

    report_path = CLAUDE_VAULT / "_system" / "_bridge_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[{now_iso}] Bridge report written: {len(lines)} lines")
    return report_path


# ─── Main ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Vault Bridge — cross-vault state sync")
    parser.add_argument("--watch", type=int, default=0,
                        help="Run continuously every N seconds (0 = run once)")
    args = parser.parse_args()

    print(f"Vault Bridge starting")
    print(f"  Claude Vault: {CLAUDE_VAULT}")
    print(f"  Hub Vault:    {HUB_VAULT}")

    if args.watch > 0:
        print(f"  Watch mode: every {args.watch}s")
        while True:
            try:
                write_bridge_report()
            except Exception as e:
                print(f"  ERROR: {e}")
            time.sleep(args.watch)
    else:
        write_bridge_report()


if __name__ == "__main__":
    main()
