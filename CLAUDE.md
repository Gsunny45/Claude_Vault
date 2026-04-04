# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Claude Vault is an AI operational layer — a persistent cognitive scaffold for Claude Code, Claude Desktop, Claude API, and local models. It is not a human notebook.

## First Steps Every Session

1. Read `_system/_briefing.md` — auto-compiled warm-start with scored notes, open tasks, recent decisions, drift warnings
2. Check `_system/_drift_report.md` — know what's stale before acting on assumptions
3. Check `Dashboard.md` in reading view — live vault state at a glance

## Vault Structure

```
_system/           Schemas, config, briefings, drift reports, query library, Prometheus exporter
_templates/        Auto-templates per folder (Templater triggers on file creation)
_scripts/          User script functions for Templater (next_id, estimate_tokens, vault_stats)
decisions/         WHY choices were made — DEC-NNNN with supersession chains
sessions/          Session logs + daily/ and weekly/ periodic notes
knowledge/         Cached analysis and architectural understanding — KNW-NNNN
tasks/             Cross-session work tracking — TSK-NNNN
inbox/             Quick timestamped captures
Dashboard.md       Live Dataview dashboard with Meta Bind action buttons
Vault_Health.md    Deep health metrics — schema compliance, freshness, tokens, links
Task_Board.md      Kanban view of task pipeline
```

## Frontmatter Schema

Every note has typed YAML frontmatter. Schemas defined in `_system/_schemas.yaml`.

| Type | Required Fields |
|------|----------------|
| decision | type, id, title, date, status, context, alternatives, rationale |
| session | type, id, date, agent, status |
| knowledge | type, id, subject, confidence, last_verified |
| task | type, id, title, status, created |
| briefing | type, compiled, token_budget, token_actual, scope |

## ID Conventions

- Decisions: `DEC-NNNN` (auto-increment via `tp.user.next_id("DEC", "decisions")`)
- Knowledge: `KNW-NNNN`
- Tasks: `TSK-NNNN`
- Sessions: `SES-YYYY-MM-DD-NNN`

## Custom Plugins

Three custom Obsidian plugins in `.obsidian/plugins/`:

- **context-compiler** — scores notes by recency/change/centrality/importance, compiles token-budgeted briefing
- **decision-ledger** — modal for structured decisions, supersession chains, index builder
- **drift-detector** — four scanners (stale refs, orphans, schema violations, contradictions)

## Rules for AI Agents

1. **Read before writing.** Check if a knowledge entry or decision already covers your topic.
2. **Log decisions.** Non-obvious choices go in `decisions/` with alternatives and rationale.
3. **Update frontmatter.** Every note you touch gets its `last_verified` or `updated` field refreshed.
4. **Use templates.** Creating a note in decisions/, knowledge/, tasks/, or sessions/ auto-applies the right template.
5. **Never delete files** without explicit user confirmation.
6. **Estimate tokens.** Set the `tokens` frontmatter field on notes you create (content.length / 4).
7. **Mark confidence.** Knowledge entries should be `verified` (you read the source), `inferred` (you derived it), or `stale` (you suspect it's outdated).

## Ecosystem Context

This vault is part of a three-vault system:

| Vault | Path | Role |
|-------|------|------|
| **Claude Vault** | `C:\Users\MarsBase\Documents\Claude_Vault` | AI operational layer (this vault) |
| **Local-Network-Hub** | `C:\Users\MarsBase\Documents\Local-Network-Hub` | Human-AI coordination, REST API on port 27124 |
| **Force Multiplication v1** | `C:\Users\MarsBase\Documents\Force Multiplication v1` | Human knowledge base (1,600+ files) |

## Monitoring

Prometheus exporter at `_system/vault_exporter.py` exposes metrics on port 9090. Tracks note counts, freshness, drift severity, task pipeline, decision velocity, knowledge health across both Claude Vault and Local-Network-Hub.

## Commands Cheat Sheet

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+B` | Compile Briefing |
| `Ctrl+Shift+D` | Run Drift Scan |
| `Ctrl+Shift+N` | New Decision |
| `Ctrl+Shift+T` | New Task |
| `Ctrl+Shift+K` | New Knowledge |
| `Ctrl+Shift+S` | New Session |
| `Ctrl+Shift+C` | Quick Capture |
