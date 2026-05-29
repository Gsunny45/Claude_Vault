# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

**Last architecture correction:** 2026-04-19 — see [[decisions/DEC-0003]].

## What This Is

**Claude_Vault** is the AI operational layer — a persistent cognitive scaffold for Codex, Codex Desktop, Codex API, and local models. It stores decisions, knowledge, sessions, and tasks for AI agents. It is **not** a human notebook, **not** a monitoring vault, **not** a knowledge-retrieval (RAG) vault.

## Ecosystem — 4-Vault Architecture

| Vault | Path | Role | Repo |
|-------|------|------|------|
| **Claude_Vault** (this) | `C:\Users\MarsBase\Documents\Claude_Vault` | AI operational layer — decisions, knowledge, sessions, tasks for AI agents | `github.com/Gsunny45/Claude_Vault` |
| **Command_Vault** | `C:\Users\MarsBase\Documents\Command_Vault` | Monitoring / observability — reads all vaults, writes health reports, dashboards, alerts. The control plane. | EXISTS on disk — repo not yet initialized (2026-05-29) |
| **Local-Network-Hub** | `C:\Users\MarsBase\Documents\Local-Network-Hub` | Orchestration — REST API, webhooks, routes work between vaults and agents | EXISTS — `github.com/Gsunny45/Local-Network-Hub` |
| **RAG_Vault** | `C:\Users\MarsBase\Documents\RAG_Vault` | Knowledge base for retrieval (replaces the role Force Multiplication v1 was filling) | EXISTS on disk — repo not yet initialized (2026-05-29) |

**Explicitly not part of this system:**
- `Force Multiplication v1` — legacy human knowledge base. Read-only reference; do NOT index, link, or include in agent context.
- `android-ai-keyboard-harness` injection keyboard (FlorisBoard fork, app "HermeticA-Z") — **active project** (un-iceboxed 2026-05-28, see [[decisions/DEC-0004]]; go-live 2026-05-29, see [[decisions/DEC-0005]]). Lives at `C:\Users\MarsBase\Documents\android-ai-keyboard-harness\` (non-vault folder, its own repo `github.com/Gsunny45/android-ai-keyboard-harness`). NOT part of the vault system; its code does not belong in Claude_Vault. The old `agentA-Z` name / `Documents\agentA-Z\` path was never scaffolded — superseded by the harness name.

## First Steps Every Session

1. Read `_system/_briefing.md` — auto-compiled warm-start with scored notes, open tasks, recent decisions, drift warnings
2. Check `_system/_drift_report.md` — know what's stale before acting on assumptions
3. Check `Dashboard.md` in reading view — live vault state at a glance
4. If the briefing/drift report is >24h old, recompile before trusting it (`Ctrl+Shift+B`, `Ctrl+Shift+D`)

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
memory/            Working memory — glossary, projects, context
Dashboard.md       Live Dataview dashboard with Meta Bind action buttons
Vault_Health.md    Deep health metrics — schema compliance, freshness, tokens, links
Task_Board.md      Kanban view of task pipeline
```

### Folders that do NOT belong here (repo hygiene)

These are currently nested inside Claude_Vault but are separate projects and must be extracted to sibling folders with their own repos. See [[knowledge/KNW-0022]] for the extraction plan.

- `llm-orchestrator/` — standalone project, no git yet. Target: `C:\Users\MarsBase\Documents\llm-orchestrator\` + new repo.
- `Claude_on_Claude/` — already has its own remote (`github.com/Gsunny45/Claude_on_Claude.git`), but is nested. Target: extract to `C:\Users\MarsBase\Documents\Claude_on_Claude\`.
- `n8n-workflows/` — belongs in Local-Network-Hub (orchestration).
- `C:\Users\MarsBase\Documents\Claude_Vault\` (literal-path ghost directory) — bug: `vault_monitor.py` writes to this string when run in WSL. Contains misrouted monitor logs only. Do not delete until logs are merged into `_system/logs/`.

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

Scan exclusions live in `_system/vault_config.yaml` under `scan_excludes`. Always exclude: `node_modules`, `llm-orchestrator`, `Claude_on_Claude`, `.obsidian`, `.smart-env`, the literal `C:\Users\MarsBase\Documents\Claude_Vault` ghost dir.

## Rules for AI Agents

1. **Read before writing.** Check if a knowledge entry or decision already covers your topic.
2. **Log decisions.** Non-obvious choices go in `decisions/` with alternatives and rationale.
3. **Update frontmatter.** Every note you touch gets its `last_verified` or `updated` field refreshed.
4. **Use templates.** Creating a note in decisions/, knowledge/, tasks/, or sessions/ auto-applies the right template.
5. **Never delete files** without explicit user confirmation.
6. **Estimate tokens.** Set the `tokens` frontmatter field on notes you create (content.length / 4).
7. **Mark confidence.** Knowledge entries should be `verified` (you read the source), `inferred` (you derived it), or `stale` (you suspect it's outdated).
8. **Respect vault boundaries.** If the work belongs in Command_Vault (monitoring), Local-Network-Hub (orchestration), or RAG_Vault (knowledge retrieval), create it there, not here.
9. **Training-data logs are gold.** Shell/session logs from Android (Termux/Alpine/Kali) and PowerShell (WSL/Kali) are preserved for model training. Do not prune or overwrite `_system/logs/`, `llm-orchestrator/training_data/`, or session transcripts without explicit confirmation.

## Monitoring

Prometheus exporter at `_system/vault_exporter.py` exposes metrics on port 9090. Tracks note counts, freshness, drift severity, task pipeline, decision velocity, knowledge health. The exporter's cross-vault scanning is the ancestor of Command_Vault — will migrate there once Command_Vault is scaffolded.

Known bug: `vault_monitor.py` writes output to a literal `C:\Users\MarsBase\Documents\Claude_Vault\_system\logs\` string that becomes a folder name under WSL. Fix pending — see [[knowledge/KNW-0022]].

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
