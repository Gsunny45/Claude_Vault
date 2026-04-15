#!/usr/bin/env python3
"""
Token Monitor — tracks token usage across agents and providers.

Reads from:
    - vault_monitor event log (file change volumes as proxy for agent activity)
    - llm-orchestrator logs (actual API token counts when available)
    - Manual entries via CLI

Outputs:
    - _system/logs/token_usage.jsonl     (append-only ledger)
    - _system/_token_state.json          (current period summary)
    - stdout summary

Usage:
    python token_monitor.py log --provider openrouter --model llama-4 --input 1200 --output 800 --cost 0.0
    python token_monitor.py log --provider claude --model opus --input 5000 --output 3000 --cost 0.15
    python token_monitor.py summary                     # print current period stats
    python token_monitor.py summary --period 7          # last 7 days
    python token_monitor.py reset                       # archive and start fresh period

Designed for DESKTOP-SH8JARJ: ~5 MB RSS, pure stdlib, no external deps.
"""

import os
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional

# ─── Configuration ──────────────────────────────────────────────

CLAUDE_VAULT = Path(os.environ.get(
    "CLAUDE_VAULT",
    r"C:\Users\MarsBase\Documents\Claude_Vault"
))


def _log_dir(vault: Path) -> Path:
    return vault / "_system" / "logs"

def _usage_log(vault: Path) -> Path:
    return _log_dir(vault) / "token_usage.jsonl"

def _state_file(vault: Path) -> Path:
    return vault / "_system" / "_token_state.json"


# ─── Logging ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("token_monitor")


# ─── Usage Entry ────────────────────────────────────────────────

def log_usage(vault: Path, provider: str, model: str,
              input_tokens: int, output_tokens: int,
              cost: float = 0.0, agent: str = "manual",
              task_id: str = "", metadata: Optional[dict] = None):
    """Append a single usage entry to the JSONL ledger."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": cost,
        "agent": agent,
        "task_id": task_id,
    }
    if metadata:
        entry["metadata"] = metadata

    log_path = _usage_log(vault)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    log.info(f"LOG  {provider}/{model}  in={input_tokens} out={output_tokens} "
             f"cost=${cost:.4f}  agent={agent}")
    return entry


# ─── Summary Engine ─────────────────────────────────────────────

def read_entries(vault: Path, days: int = 1) -> list[dict]:
    """Read JSONL entries from the last N days."""
    log_path = _usage_log(vault)
    if not log_path.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry["timestamp"])
                if ts >= cutoff:
                    entries.append(entry)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
    return entries


def compute_summary(entries: list[dict]) -> dict:
    """Aggregate token usage by provider, model, and agent."""
    totals = {
        "total_input": 0, "total_output": 0, "total_tokens": 0,
        "total_cost": 0.0, "request_count": len(entries),
    }
    by_provider: dict[str, dict] = {}
    by_model: dict[str, dict] = {}
    by_agent: dict[str, dict] = {}

    for e in entries:
        inp = e.get("input_tokens", 0)
        out = e.get("output_tokens", 0)
        cost = e.get("cost_usd", 0.0)
        totals["total_input"] += inp
        totals["total_output"] += out
        totals["total_tokens"] += inp + out
        totals["total_cost"] += cost

        for key, bucket in [(e.get("provider", "?"), by_provider),
                             (e.get("model", "?"), by_model),
                             (e.get("agent", "?"), by_agent)]:
            if key not in bucket:
                bucket[key] = {"input": 0, "output": 0, "cost": 0.0, "count": 0}
            bucket[key]["input"] += inp
            bucket[key]["output"] += out
            bucket[key]["cost"] += cost
            bucket[key]["count"] += 1

    return {
        "period_entries": len(entries),
        "totals": totals,
        "by_provider": by_provider,
        "by_model": by_model,
        "by_agent": by_agent,
    }


def write_state(vault: Path, summary: dict, period_days: int):
    """Write current summary to state file."""
    state = {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "period_days": period_days,
        **summary,
    }
    state_path = _state_file(vault)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return state


def print_summary(summary: dict, period_days: int):
    """Human-readable summary to stdout."""
    t = summary["totals"]
    print(f"\n{'='*50}")
    print(f" Token Usage Summary (last {period_days} day{'s' if period_days != 1 else ''})")
    print(f"{'='*50}")
    print(f" Requests:     {t['request_count']}")
    print(f" Input tokens: {t['total_input']:,}")
    print(f" Output tokens:{t['total_output']:,}")
    print(f" Total tokens: {t['total_tokens']:,}")
    print(f" Total cost:   ${t['total_cost']:.4f}")
    print()

    if summary["by_provider"]:
        print(" By Provider:")
        for name, stats in sorted(summary["by_provider"].items()):
            print(f"   {name:20s}  {stats['count']:3d} reqs  "
                  f"{stats['input']+stats['output']:>10,} tok  ${stats['cost']:.4f}")
        print()

    if summary["by_agent"]:
        print(" By Agent:")
        for name, stats in sorted(summary["by_agent"].items()):
            print(f"   {name:20s}  {stats['count']:3d} reqs  "
                  f"{stats['input']+stats['output']:>10,} tok")
        print()


# ─── Archive / Reset ────────────────────────────────────────────

def archive_and_reset(vault: Path):
    """Move current log to timestamped archive, start fresh."""
    log_path = _usage_log(vault)
    if not log_path.exists():
        log.info("Nothing to archive")
        return

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_path = log_path.parent / f"token_usage_{ts}.jsonl"
    log_path.rename(archive_path)
    log.info(f"Archived to {archive_path.name}")

    # Clear state
    state_path = _state_file(vault)
    if state_path.exists():
        state_path.unlink()


# ─── Main ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Token Monitor — track LLM token usage across agents"
    )
    parser.add_argument("--vault", type=str, default=str(CLAUDE_VAULT))
    sub = parser.add_subparsers(dest="command")

    # log subcommand
    log_cmd = sub.add_parser("log", help="Record a usage entry")
    log_cmd.add_argument("--provider", required=True)
    log_cmd.add_argument("--model", required=True)
    log_cmd.add_argument("--input", type=int, required=True, dest="input_tokens")
    log_cmd.add_argument("--output", type=int, required=True, dest="output_tokens")
    log_cmd.add_argument("--cost", type=float, default=0.0)
    log_cmd.add_argument("--agent", default="manual")
    log_cmd.add_argument("--task-id", default="")

    # summary subcommand
    sum_cmd = sub.add_parser("summary", help="Show usage summary")
    sum_cmd.add_argument("--period", type=int, default=1, help="Days to summarize")

    # reset subcommand
    sub.add_parser("reset", help="Archive current log, start fresh")

    args = parser.parse_args()
    vault = Path(args.vault)

    if args.command == "log":
        log_usage(vault, args.provider, args.model,
                  args.input_tokens, args.output_tokens,
                  args.cost, args.agent, args.task_id)

    elif args.command == "summary":
        entries = read_entries(vault, args.period)
        summary = compute_summary(entries)
        write_state(vault, summary, args.period)
        print_summary(summary, args.period)

    elif args.command == "reset":
        archive_and_reset(vault)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
