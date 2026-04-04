#!/usr/bin/env python3
"""
Prometheus metrics exporter for Obsidian vaults.

Exposes vault health, note counts, freshness, task pipeline, decision tracking,
knowledge health, drift status, and session activity on port 9090 at /metrics.

Dependencies: prometheus_client (pip install prometheus_client)
"""

import os
import re
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

from prometheus_client import start_http_server, Gauge

# ---------------------------------------------------------------------------
# Configuration — override via environment variables
# ---------------------------------------------------------------------------

VAULTS = {
    "claude_vault": Path(
        os.environ.get("VAULT_CLAUDE", r"C:\Users\MarsBase\Documents\Claude_Vault")
    ),
    "local_network_hub": Path(
        os.environ.get(
            "VAULT_LNH", r"C:\Users\MarsBase\Documents\Local-Network-Hub"
        )
    ),
}

SCRAPE_INTERVAL = int(os.environ.get("SCRAPE_INTERVAL", "60"))
STALE_THRESHOLD_DAYS = int(os.environ.get("STALE_THRESHOLD_DAYS", "14"))
EXPORTER_PORT = int(os.environ.get("EXPORTER_PORT", "9090"))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("vault_exporter")

# ---------------------------------------------------------------------------
# Prometheus metrics definitions
# ---------------------------------------------------------------------------

# Note counts
NOTES_TOTAL = Gauge(
    "vault_notes_total",
    "Count of .md files per top-level folder",
    ["vault", "folder"],
)
NOTES_BY_STATUS = Gauge(
    "vault_notes_by_status",
    "Count of notes by frontmatter status field",
    ["vault", "status"],
)
NOTES_BY_TYPE = Gauge(
    "vault_notes_by_type",
    "Count of notes by frontmatter type field",
    ["vault", "type"],
)

# Freshness
NOTE_OLDEST_MODIFIED = Gauge(
    "vault_note_oldest_modified_seconds",
    "Age in seconds of the least recently modified note",
    ["vault"],
)
NOTE_NEWEST_MODIFIED = Gauge(
    "vault_note_newest_modified_seconds",
    "Age in seconds of the most recently modified note",
    ["vault"],
)
STALE_NOTES = Gauge(
    "vault_stale_notes_total",
    "Count of notes not modified in more than 14 days",
    ["vault"],
)

# Knowledge health (Claude Vault specific)
KNOWLEDGE_VERIFIED = Gauge(
    "vault_knowledge_verified_total",
    "Knowledge notes with confidence=verified",
)
KNOWLEDGE_STALE = Gauge(
    "vault_knowledge_stale_total",
    "Knowledge notes with confidence=stale",
)
KNOWLEDGE_INFERRED = Gauge(
    "vault_knowledge_inferred_total",
    "Knowledge notes with confidence=inferred",
)

# Decision tracking (Claude Vault specific)
DECISIONS_TOTAL = Gauge(
    "vault_decisions_total",
    "Decisions by status",
    ["status"],
)
DECISION_CHAIN_LENGTH = Gauge(
    "vault_decision_chain_length",
    "Longest supersession chain in decisions",
)

# Task pipeline
TASKS_TOTAL = Gauge(
    "vault_tasks_total",
    "Tasks by status",
    ["vault", "status"],
)
TASKS_OLDEST_OPEN_DAYS = Gauge(
    "vault_tasks_oldest_open_days",
    "Age in days of the oldest open task",
    ["vault"],
)

# Drift (Claude Vault specific)
DRIFT_ISSUES = Gauge(
    "vault_drift_issues_total",
    "Issues by severity from last drift scan",
    ["severity"],
)
DRIFT_LAST_SCAN = Gauge(
    "vault_drift_last_scan_timestamp",
    "Unix timestamp of last drift scan",
)

# Session activity
SESSIONS_TOTAL = Gauge(
    "vault_sessions_total",
    "Total session note count",
    ["vault"],
)
SESSIONS_LAST_7_DAYS = Gauge(
    "vault_sessions_last_7_days",
    "Sessions created in last 7 days",
    ["vault"],
)

# Vault size
TOTAL_FILES = Gauge(
    "vault_total_files",
    "Total file count in the vault",
    ["vault"],
)
TOTAL_SIZE_BYTES = Gauge(
    "vault_total_size_bytes",
    "Total size of all .md files in bytes",
    ["vault"],
)

# ---------------------------------------------------------------------------
# Frontmatter parser  (no external YAML dependency)
# ---------------------------------------------------------------------------

_FM_FENCE = re.compile(r"^---\s*\r?\n", re.MULTILINE)


def parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from markdown text into a flat dict.

    Handles simple key: value pairs and recognises quoted strings, bare
    scalars, and list items that begin with ``- ``.  Nested maps are not
    expanded — only top-level keys matter for metrics.
    """
    m = _FM_FENCE.search(text)
    if not m:
        return {}
    start = m.end()
    m2 = _FM_FENCE.search(text, start)
    if not m2:
        return {}
    block = text[start : m2.start()]

    result: dict = {}
    current_key = None
    current_list = None

    for raw_line in block.splitlines():
        line = raw_line.rstrip()

        # List continuation
        if current_list is not None and re.match(r"^\s+-\s+", line):
            val = re.sub(r"^\s+-\s+", "", line).strip().strip("\"'")
            current_list.append(val)
            continue
        else:
            if current_list is not None:
                result[current_key] = current_list
                current_list = None
                current_key = None

        kv = re.match(r"^([A-Za-z_][\w_-]*)\s*:\s*(.*)", line)
        if not kv:
            continue
        key = kv.group(1).strip()
        val = kv.group(2).strip()

        if val == "" or val == "[]":
            # Could be start of a list block or empty value
            current_key = key
            current_list = []
            continue

        # Strip surrounding quotes
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]

        result[key] = val
        current_key = None
        current_list = None

    # Flush trailing list
    if current_list is not None and current_key is not None:
        result[current_key] = current_list

    return result


def read_frontmatter(path: Path) -> dict:
    """Read a markdown file and return its frontmatter dict, or {} on error."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return parse_frontmatter(text)
    except OSError as exc:
        log.debug("Could not read %s: %s", path, exc)
        return {}


# ---------------------------------------------------------------------------
# Vault scanning helpers
# ---------------------------------------------------------------------------


def iter_md_files(vault_root: Path):
    """Yield all .md file paths under *vault_root*, skipping .obsidian."""
    for dirpath, dirnames, filenames in os.walk(vault_root):
        # Skip hidden / Obsidian config dirs
        dirnames[:] = [
            d for d in dirnames if not d.startswith(".") and d != "node_modules"
        ]
        for fn in filenames:
            if fn.lower().endswith(".md"):
                yield Path(dirpath) / fn


def top_level_folder(vault_root: Path, file_path: Path) -> str:
    """Return the top-level folder name relative to the vault, or '_root'."""
    try:
        rel = file_path.relative_to(vault_root)
    except ValueError:
        return "_root"
    parts = rel.parts
    if len(parts) <= 1:
        return "_root"
    return parts[0]


def parse_iso_date(s: str) -> datetime | None:
    """Best-effort parse of ISO date / datetime strings from frontmatter."""
    if not s:
        return None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Collection logic
# ---------------------------------------------------------------------------


def collect_vault(vault_label: str, vault_root: Path):
    """Scan one vault and update Prometheus gauges."""
    if not vault_root.is_dir():
        log.warning("Vault path does not exist: %s", vault_root)
        return

    now = time.time()
    now_dt = datetime.now(tz=timezone.utc)
    stale_cutoff = now - (STALE_THRESHOLD_DAYS * 86400)
    seven_days_ago = now_dt.timestamp() - 7 * 86400

    folder_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    task_status_counts: dict[str, int] = {}

    oldest_mtime = float("inf")
    newest_mtime = 0.0
    stale_count = 0
    total_files = 0
    total_md_size = 0

    session_total = 0
    session_recent = 0

    oldest_open_task_days: float | None = None

    # Knowledge / Decision accumulators (Claude Vault only)
    knowledge_confidence: dict[str, int] = {}
    decision_statuses: dict[str, int] = {}
    decision_supersedes: dict[str, str] = {}  # id -> supersedes id

    for md_path in iter_md_files(vault_root):
        total_files += 1
        try:
            st = md_path.stat()
            sz = st.st_size
            mtime = st.st_mtime
        except OSError:
            continue
        total_md_size += sz

        if mtime < oldest_mtime:
            oldest_mtime = mtime
        if mtime > newest_mtime:
            newest_mtime = mtime
        if mtime < stale_cutoff:
            stale_count += 1

        folder = top_level_folder(vault_root, md_path)
        folder_counts[folder] = folder_counts.get(folder, 0) + 1

        fm = read_frontmatter(md_path)
        if not fm:
            continue

        # Status / type aggregation
        s = fm.get("status", "")
        if s:
            status_counts[s] = status_counts.get(s, 0) + 1
        t = fm.get("type", "")
        if t:
            type_counts[t] = type_counts.get(t, 0) + 1

        # Sessions
        if t == "session":
            session_total += 1
            date_str = fm.get("date", "")
            dt = parse_iso_date(date_str)
            if dt and dt.timestamp() >= seven_days_ago:
                session_recent += 1

        # Tasks
        if t == "task":
            ts = fm.get("status", "unknown")
            task_status_counts[ts] = task_status_counts.get(ts, 0) + 1
            if ts in ("open", "in_progress", "blocked"):
                created_str = fm.get("created", "")
                cdt = parse_iso_date(created_str)
                if cdt:
                    age_days = (now_dt - cdt).total_seconds() / 86400
                    if oldest_open_task_days is None or age_days > oldest_open_task_days:
                        oldest_open_task_days = age_days

        # Claude-Vault-specific: knowledge confidence
        if vault_label == "claude_vault" and t == "knowledge":
            conf = fm.get("confidence", "unknown")
            knowledge_confidence[conf] = knowledge_confidence.get(conf, 0) + 1

        # Claude-Vault-specific: decisions
        if vault_label == "claude_vault" and t == "decision":
            ds = fm.get("status", "unknown")
            decision_statuses[ds] = decision_statuses.get(ds, 0) + 1
            dec_id = fm.get("id", "")
            supersedes = fm.get("supersedes", "")
            if dec_id and supersedes:
                decision_supersedes[dec_id] = supersedes

    # --- Write gauges ---

    # Folder counts
    for folder, count in folder_counts.items():
        NOTES_TOTAL.labels(vault=vault_label, folder=folder).set(count)

    # Status / type counts
    for s, count in status_counts.items():
        NOTES_BY_STATUS.labels(vault=vault_label, status=s).set(count)
    for t, count in type_counts.items():
        NOTES_BY_TYPE.labels(vault=vault_label, type=t).set(count)

    # Freshness
    if oldest_mtime < float("inf"):
        NOTE_OLDEST_MODIFIED.labels(vault=vault_label).set(now - oldest_mtime)
    if newest_mtime > 0:
        NOTE_NEWEST_MODIFIED.labels(vault=vault_label).set(now - newest_mtime)
    STALE_NOTES.labels(vault=vault_label).set(stale_count)

    # Tasks
    for ts, count in task_status_counts.items():
        TASKS_TOTAL.labels(vault=vault_label, status=ts).set(count)
    TASKS_OLDEST_OPEN_DAYS.labels(vault=vault_label).set(
        oldest_open_task_days if oldest_open_task_days is not None else 0
    )

    # Sessions
    SESSIONS_TOTAL.labels(vault=vault_label).set(session_total)
    SESSIONS_LAST_7_DAYS.labels(vault=vault_label).set(session_recent)

    # Vault size
    TOTAL_FILES.labels(vault=vault_label).set(total_files)
    TOTAL_SIZE_BYTES.labels(vault=vault_label).set(total_md_size)

    # Claude-Vault-specific gauges
    if vault_label == "claude_vault":
        KNOWLEDGE_VERIFIED.set(knowledge_confidence.get("verified", 0))
        KNOWLEDGE_STALE.set(knowledge_confidence.get("stale", 0))
        KNOWLEDGE_INFERRED.set(knowledge_confidence.get("inferred", 0))

        for ds in ("accepted", "superseded", "proposed", "rejected"):
            DECISIONS_TOTAL.labels(status=ds).set(decision_statuses.get(ds, 0))

        # Longest supersession chain
        chain_len = _longest_chain(decision_supersedes)
        DECISION_CHAIN_LENGTH.set(chain_len)

    log.info(
        "Collected %s: %d files, %d bytes, %d stale",
        vault_label,
        total_files,
        total_md_size,
        stale_count,
    )


def _longest_chain(supersedes: dict[str, str]) -> int:
    """Compute the longest supersession chain from a dict of id -> supersedes_id."""
    if not supersedes:
        return 0
    # Build reverse index: superseded_by[old] = new
    all_ids = set(supersedes.keys()) | set(supersedes.values())
    # Walk forward from each root
    children: dict[str, str] = {}  # old -> new (the one that supersedes it)
    for new_id, old_id in supersedes.items():
        children[old_id] = new_id

    best = 0
    for start in all_ids:
        length = 1
        node = start
        visited = {node}
        while node in children:
            node = children[node]
            if node in visited:
                break  # cycle guard
            visited.add(node)
            length += 1
        if length > best:
            best = length
    return best


def collect_drift():
    """Parse _system/_drift_report.md frontmatter for drift metrics."""
    drift_path = VAULTS.get("claude_vault", Path()) / "_system" / "_drift_report.md"
    if not drift_path.is_file():
        log.debug("Drift report not found: %s", drift_path)
        return

    fm = read_frontmatter(drift_path)
    if not fm:
        return

    for severity in ("critical", "high", "medium", "low"):
        val = fm.get(severity, "0")
        try:
            DRIFT_ISSUES.labels(severity=severity).set(int(val))
        except (ValueError, TypeError):
            DRIFT_ISSUES.labels(severity=severity).set(0)

    scanned_str = fm.get("scanned", "")
    dt = parse_iso_date(scanned_str)
    if dt:
        DRIFT_LAST_SCAN.set(dt.timestamp())

    log.info(
        "Collected drift: %s issues (%s critical, %s high, %s medium, %s low)",
        fm.get("issues_found", "?"),
        fm.get("critical", "0"),
        fm.get("high", "0"),
        fm.get("medium", "0"),
        fm.get("low", "0"),
    )


# ---------------------------------------------------------------------------
# Main collection loop
# ---------------------------------------------------------------------------


def collection_loop():
    """Blocking loop that collects metrics on the configured interval."""
    while True:
        log.info("Starting collection cycle")
        try:
            for label, root in VAULTS.items():
                collect_vault(label, root)
            collect_drift()
        except Exception:
            log.exception("Unhandled error during collection cycle")
        log.info("Collection cycle complete. Sleeping %ds.", SCRAPE_INTERVAL)
        time.sleep(SCRAPE_INTERVAL)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    log.info("Vault exporter starting on port %d", EXPORTER_PORT)
    log.info("Scrape interval: %ds | Stale threshold: %d days", SCRAPE_INTERVAL, STALE_THRESHOLD_DAYS)
    for label, root in VAULTS.items():
        log.info("  %s -> %s (exists: %s)", label, root, root.is_dir())

    # Start Prometheus HTTP server
    start_http_server(EXPORTER_PORT)
    log.info("HTTP server listening on http://localhost:%d/metrics", EXPORTER_PORT)

    # Run first collection immediately, then loop
    collection_loop()
