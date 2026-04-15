#!/usr/bin/env python3
"""
Vault Monitor — watches Claude Vault for filesystem changes and emits
structured events for downstream consumers (task_router, token_monitor).

Modes:
    python vault_monitor.py                 # watchdog mode (requires pip install watchdog)
    python vault_monitor.py --poll 5        # polling fallback, check every 5s
    python vault_monitor.py --once          # single snapshot, print and exit

Events are:
    1. Logged to _system/logs/vault_monitor.jsonl  (append-only, one JSON object per line)
    2. Written to _system/_monitor_state.json       (latest snapshot for other scripts to read)
    3. Printed to stdout for piping

Designed to run as a background process on DESKTOP-SH8JARJ.
Lightweight: ~15 MB RSS, no GPU, minimal CPU on idle.
"""

import os
import re
import sys
import json
import time
import signal
import hashlib
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

WATCHED_FOLDERS = ["tasks", "decisions", "knowledge", "inbox", "sessions"]
IGNORED_PATTERNS = [".obsidian", "_templates", ".git", "__pycache__", "node_modules"]

POLL_INTERVAL = int(os.environ.get("VAULT_POLL_INTERVAL", "5"))


def _log_dir(vault: Path) -> Path:
    return vault / "_system" / "logs"

def _event_log(vault: Path) -> Path:
    return _log_dir(vault) / "vault_monitor.jsonl"

def _state_file(vault: Path) -> Path:
    return vault / "_system" / "_monitor_state.json"

# ─── Logging ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("vault_monitor")

# ─── Frontmatter Parser (shared with vault_bridge.py) ──────────

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


def file_hash(filepath: Path) -> str:
    """Fast content hash (first 16KB) for change detection."""
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read(16384)).hexdigest()
    except (OSError, IOError):
        return ""


# ─── Snapshot Engine ────────────────────────────────────────────

class VaultSnapshot:
    """Point-in-time snapshot of watched vault files."""

    def __init__(self, vault_path: Path, folders: list[str]):
        self.vault = vault_path
        self.folders = folders
        self.files: dict[str, dict] = {}  # rel_path -> {mtime, size, hash, frontmatter}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def scan(self) -> "VaultSnapshot":
        """Walk watched folders and capture file metadata."""
        for folder in self.folders:
            folder_path = self.vault / folder
            if not folder_path.exists():
                continue
            for md in folder_path.rglob("*.md"):
                rel = md.relative_to(self.vault).as_posix()
                if any(ign in rel for ign in IGNORED_PATTERNS):
                    continue
                stat = md.stat()
                self.files[rel] = {
                    "mtime": stat.st_mtime,
                    "size": stat.st_size,
                    "hash": file_hash(md),
                    "frontmatter": parse_frontmatter(md),
                }
        return self

    def diff(self, previous: Optional["VaultSnapshot"]) -> list[dict]:
        """Compare against a previous snapshot. Returns list of change events."""
        if previous is None:
            return [{"type": "initial_scan", "file_count": len(self.files),
                     "timestamp": self.timestamp}]

        events = []
        prev_files = previous.files
        curr_files = self.files

        # New files
        for rel in set(curr_files) - set(prev_files):
            fm = curr_files[rel]["frontmatter"]
            events.append({
                "type": "created",
                "path": rel,
                "timestamp": self.timestamp,
                "note_type": fm.get("type", "unknown"),
                "note_id": fm.get("id", ""),
                "note_status": fm.get("status", ""),
            })

        # Deleted files
        for rel in set(prev_files) - set(curr_files):
            events.append({
                "type": "deleted",
                "path": rel,
                "timestamp": self.timestamp,
            })

        # Modified files (hash changed)
        for rel in set(curr_files) & set(prev_files):
            if curr_files[rel]["hash"] != prev_files[rel]["hash"]:
                fm = curr_files[rel]["frontmatter"]
                old_fm = prev_files[rel]["frontmatter"]
                # Track status transitions
                status_change = None
                if fm.get("status") != old_fm.get("status"):
                    status_change = {
                        "from": old_fm.get("status", ""),
                        "to": fm.get("status", ""),
                    }
                events.append({
                    "type": "modified",
                    "path": rel,
                    "timestamp": self.timestamp,
                    "note_type": fm.get("type", "unknown"),
                    "note_id": fm.get("id", ""),
                    "status_change": status_change,
                    "size_delta": curr_files[rel]["size"] - prev_files[rel]["size"],
                })

        return events

    def summary(self) -> dict:
        """Aggregate stats for the state file."""
        by_folder: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for rel, meta in self.files.items():
            folder = rel.split("/")[0] if "/" in rel else "root"
            by_folder[folder] = by_folder.get(folder, 0) + 1
            status = meta["frontmatter"].get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "timestamp": self.timestamp,
            "total_files": len(self.files),
            "by_folder": by_folder,
            "by_status": by_status,
        }


# ─── Event Logger ───────────────────────────────────────────────

class EventLogger:
    """Append-only JSONL event log + state file writer."""

    def __init__(self, log_path: Path, state_path: Path):
        self.log_path = log_path
        self.state_path = state_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_events(self, events: list[dict]):
        """Append events to JSONL log."""
        if not events:
            return
        with open(self.log_path, "a", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event, default=str) + "\n")
        for ev in events:
            etype = ev.get("type", "?")
            path = ev.get("path", "")
            if etype == "initial_scan":
                log.info(f"INIT  {ev.get('file_count', 0)} files tracked")
            elif etype == "created":
                log.info(f"NEW   {path}  [{ev.get('note_type', '')}]")
            elif etype == "deleted":
                log.warning(f"DEL   {path}")
            elif etype == "modified":
                sc = ev.get("status_change")
                extra = f"  status: {sc['from']}→{sc['to']}" if sc else ""
                log.info(f"MOD   {path}  (Δ{ev.get('size_delta', 0):+d}b){extra}")

    def write_state(self, summary: dict):
        """Write latest snapshot summary for other scripts to read."""
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)


# ─── Watchdog Mode (preferred) ──────────────────────────────────

def try_watchdog_mode(vault: Path, logger: EventLogger) -> bool:
    """Attempt to use watchdog for real-time filesystem events. Returns False if unavailable."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler, FileSystemEvent
    except ImportError:
        log.warning("watchdog not installed — falling back to polling")
        return False

    # We still need periodic snapshots for frontmatter-level diffs
    # Watchdog gives us instant notification; snapshot gives us semantic diffs
    prev_snapshot: Optional[VaultSnapshot] = None

    class VaultHandler(FileSystemEventHandler):
        def __init__(self):
            self.dirty = True  # trigger initial scan

        def _is_relevant(self, path: str) -> bool:
            rel = Path(path).relative_to(vault).as_posix() if path.startswith(str(vault)) else path
            if any(ign in rel for ign in IGNORED_PATTERNS):
                return False
            return any(rel.startswith(f) for f in WATCHED_FOLDERS) and rel.endswith(".md")

        def on_any_event(self, event: FileSystemEvent):
            if event.is_directory:
                return
            src = getattr(event, "src_path", "")
            if self._is_relevant(src):
                self.dirty = True

    handler = VaultHandler()
    observer = Observer()
    for folder in WATCHED_FOLDERS:
        folder_path = vault / folder
        if folder_path.exists():
            observer.schedule(handler, str(folder_path), recursive=True)

    def _shutdown(sig, frame):
        log.info("Shutting down watchdog observer...")
        observer.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    observer.start()
    log.info(f"Watchdog observer started on {len(WATCHED_FOLDERS)} folders")

    nonlocal_prev = {"snapshot": None}

    try:
        while True:
            if handler.dirty:
                handler.dirty = False
                snap = VaultSnapshot(vault, WATCHED_FOLDERS).scan()
                events = snap.diff(nonlocal_prev["snapshot"])
                logger.log_events(events)
                logger.write_state(snap.summary())
                nonlocal_prev["snapshot"] = snap
            time.sleep(1)  # check dirty flag every second
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()

    return True


# ─── Polling Mode (fallback) ───────────────────────────────────

def polling_mode(vault: Path, logger: EventLogger, interval: int):
    """Poll-based monitoring. Works everywhere, no dependencies."""

    def _shutdown(sig, frame):
        log.info("Shutting down poller...")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    prev_snapshot = None
    log.info(f"Polling mode: every {interval}s on {len(WATCHED_FOLDERS)} folders")

    while True:
        try:
            snap = VaultSnapshot(vault, WATCHED_FOLDERS).scan()
            events = snap.diff(prev_snapshot)
            if events:
                logger.log_events(events)
                logger.write_state(snap.summary())
            prev_snapshot = snap
        except Exception as e:
            log.error(f"Poll cycle error: {e}")
        time.sleep(interval)


# ─── Single Scan Mode ──────────────────────────────────────────

def single_scan(vault: Path, logger: EventLogger):
    """One-shot scan: print summary and exit."""
    snap = VaultSnapshot(vault, WATCHED_FOLDERS).scan()
    events = snap.diff(None)
    logger.log_events(events)
    summary = snap.summary()
    logger.write_state(summary)
    print(json.dumps(summary, indent=2))
    return summary


# ─── Main ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Vault Monitor — filesystem watcher for Claude Vault"
    )
    parser.add_argument("--poll", type=int, default=0,
                        help="Polling interval in seconds (0 = use watchdog)")
    parser.add_argument("--once", action="store_true",
                        help="Single scan, print summary, exit")
    parser.add_argument("--vault", type=str, default=str(CLAUDE_VAULT),
                        help="Override vault path")
    args = parser.parse_args()

    vault = Path(args.vault)
    event_log = _event_log(vault)
    state_file = _state_file(vault)
    logger = EventLogger(event_log, state_file)

    log.info(f"Vault Monitor starting")
    log.info(f"  Vault: {vault}")
    log.info(f"  Watching: {', '.join(WATCHED_FOLDERS)}")
    log.info(f"  Event log: {event_log}")

    if args.once:
        single_scan(vault, logger)
        return

    if args.poll > 0:
        polling_mode(vault, logger, args.poll)
    else:
        if not try_watchdog_mode(vault, logger):
            log.info("Falling back to polling mode")
            polling_mode(vault, logger, POLL_INTERVAL)


if __name__ == "__main__":
    main()
