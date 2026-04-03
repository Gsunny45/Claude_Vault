# Claude Vault

This is not a human notebook. It is an operational layer for AI systems — Claude Code, Claude Desktop, Claude API, and local models.

## Purpose

Solve five problems that make AI sessions inefficient:

1. **Cold starts** — every session begins with expensive re-orientation
2. **Lost rationale** — code says *what*, git says *when*, nothing says *why*
3. **Self-contradiction** — without recall, AI gives conflicting guidance across sessions
4. **Redundant analysis** — the same codebase gets re-explored from scratch every time
5. **No feedback signal** — AI can't tell which outputs were useful and which were noise

## Structure

```
_system/            Schemas, config, briefings, drift reports, query library
_templates/         Auto-templates — trigger on file creation per folder
decisions/          Structured records of WHY choices were made
sessions/           Session logs + daily/ and weekly/ periodic notes
  daily/            Auto-generated daily logs with Dataview rollups
  weekly/           Weekly reviews with decision velocity + task throughput
knowledge/          Cached analysis, architecture maps, pattern libraries
tasks/              Cross-session work tracking with dependency chains
inbox/              Quick capture — timestamped entries appended throughout the day
Dashboard.md        Live Dataview dashboard — vault stats at a glance
Vault_Health.md     Deep health metrics — schema compliance, freshness, link density, tokens
```

## Design Principles

- **Machine-readable first.** Every note has typed YAML frontmatter. No decorative formatting.
- **Queryable.** Dataview can answer any structural question without scanning full text.
- **Token-aware.** Notes are sized and tagged so a context compiler can budget what to load.
- **Append-friendly.** New information adds notes; it never requires editing old ones in-place.
- **Self-healing.** Contradictions between notes are detectable and flagged, not silently stale.

## Custom Plugins (Built, Active)

| Plugin | Lines | What it does |
|--------|-------|-------------|
| **context-compiler** | 805 | On vault open: scores every note (recency, change delta, link centrality, importance), packs the best into a token-budgeted `_system/_briefing.md`. AI reads one file and is oriented. |
| **decision-ledger** | 952 | Modal for creating decisions with auto-incrementing IDs, alternatives, rationale. Supersession chains. Index builder. File-affect search. |
| **drift-detector** | 1001 | Four scanners: stale references, orphans, schema violations, contradictions. Writes `_system/_drift_report.md`. Status bar indicator. |

## Community Plugins

| Plugin | Role |
|--------|------|
| Dataview | Query engine — treats frontmatter as a database, powers both dashboards |
| Templater | Auto-applies folder templates on note creation (6 templates) |
| Local REST API | HTTP interface for external AI agents to read/write vault |
| Periodic Notes | Daily + weekly notes with Dataview rollups |
| Linter | Lint-on-save: frontmatter key ordering, trailing spaces, blank lines |
| Tag Wrangler | Controlled tag vocabulary management |
| QuickAdd | 5 macros: New Decision, New Session, New Knowledge, New Task, Quick Capture |
| Meta Bind | Inline frontmatter editing widgets |
| Commander | Toolbar buttons: Compile Briefing, Run Drift Scan, Quick Capture |
| Git | Version control for vault contents |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+B` | Compile Briefing |
| `Ctrl+Shift+D` | Run Drift Scan |
| `Ctrl+Shift+R` | Open Drift Report |
| `Ctrl+Shift+N` | New Decision |
| `Ctrl+Shift+I` | Build Decision Index |
| `Ctrl+Shift+C` | Quick Capture to Inbox |
| `Ctrl+Shift+T` | New Task |

## Graph View

Color-coded by folder: decisions (orange), sessions (blue), knowledge (green), tasks (red), system (gray). Arrows enabled, orphans visible, unresolved links hidden.
