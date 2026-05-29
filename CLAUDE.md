# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Last architecture correction:** 2026-04-19 — see [[decisions/DEC-0003]].

## What This Is

**Claude_Vault** is the AI operational layer — a persistent cognitive scaffold for Claude Code, Claude Desktop, Claude API, and local models. It stores decisions, knowledge, sessions, and tasks for AI agents. It is **not** a human notebook, **not** a monitoring vault, **not** a knowledge-retrieval (RAG) vault.

## Ecosystem — Tiered N-Vault Architecture

> Reframed 2026-05-29 ([[decisions/DEC-0006]]). The old "4-vault" label under-described
> reality (~8 vaults exist). Tiers below reflect role, not priority. Separation-of-concerns
> from [[decisions/DEC-0003]] still governs: operational ≠ monitoring ≠ orchestration ≠ retrieval.

### Core operational
| Vault | Path | Role | Repo |
|-------|------|------|------|
| **Claude_Vault** (this) | `C:\Users\MarsBase\Documents\Claude_Vault` | AI operational layer — decisions, knowledge, sessions, tasks for AI agents | `github.com/Gsunny45/Claude_Vault` |

### Supporting (control / orchestration / retrieval)
| Vault | Path | Role | Repo |
|-------|------|------|------|
| **Command_Vault** | `C:\Users\MarsBase\Documents\Command_Vault` | Monitoring / observability — reads all vaults, writes health reports, dashboards, alerts. The control plane. | `github.com/Gsunny45/Command_Vault` (init 2026-05-29) |
| **Local-Network-Hub** | `C:\Users\MarsBase\Documents\Local-Network-Hub` | Orchestration — REST API, webhooks, routes work between vaults and agents. Owns `n8n-workflows`. | `github.com/Gsunny45/Local-Network-Hub` |
| **RAG_Vault** | `C:\Users\MarsBase\Documents\RAG_Vault` | Knowledge base for retrieval (replaces the role Force Multiplication v1 was filling) | `github.com/Gsunny45/RAG_Vault` (init 2026-05-29) |

### Hermes layer / methodology / delivery
| Vault | Path | Role | Repo |
|-------|------|------|------|
| **Hermes_Vault** | `C:\Users\MarsBase\Documents\Hermes_Vault` | Hermes operational layer (read-only reference) | `github.com/Gsunny45/Hermes_Vault` |
| **Hermes_Phone_Vault** | `C:\Users\MarsBase\Documents\Hermes_Phone_Vault` | Device ops | local-only |
| **Vault_Skills** | `C:\Users\MarsBase\Documents\Vault_Skills` | Build methodology / design system | `github.com/Gsunny45/Vault_Skills` |
| **Hermes_Drop_vault** | `C:\Users\MarsBase\Desktop\Hermes_Drop_vault` | File delivery target (default output) | local-only |

### Boundary project (NOT a vault)
| Entity | Path | Role | Repo |
|--------|------|------|------|
| **android-ai-keyboard-harness** | `C:\Users\MarsBase\Documents\android-ai-keyboard-harness` | Injection keyboard (FlorisBoard fork, app "HermeticA-Z"). Active (DEC-0004); go-live 2026-05-29 (DEC-0005). Holds the canonical **Hermetic_A-Z_Vault** visual authority at `...\android-ai-keyboard-harness\Hermetic_A-Z_Vault`. | `github.com/Gsunny45/android-ai-keyboard-harness` |

**Explicitly not part of this system:**
- `Force Multiplication v1` — legacy human knowledge base. **Permanently excluded** from the agent system ([[decisions/DEC-0006]]): read-only reference, do NOT index, link, or include in agent context. No FM v1 → RAG ingestion.
- **Keyboard boundary:** the harness is NOT a vault; its code/internals do not belong in Claude_Vault and are not pulled into active briefings. Only keyboard knowledge/handoff pointers ([[knowledge/KNW-0024]], [[knowledge/KNW-0008]], [[knowledge/KNW-0025-keyboard-vault-injection-tests]]) live here. The `agentA-Z` name / `Documents\agentA-Z\` path was never scaffolded — superseded by the harness name.
- **Visual authority:** canonical Hermetic_A-Z brand/palette assets live under the harness path above. The `C:\Users\MarsBase\Pictures\Hermetic_A-Z_Vault` path named in older docs does not exist and is retired.

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

**RESOLVED 2026-05-29** ([[decisions/DEC-0006]], [[knowledge/KNW-0026]]). All four hygiene items are cleared:

- `llm-orchestrator/` — ✅ extracted (no longer nested).
- `Claude_on_Claude/` — ✅ extracted (no longer nested).
- `n8n-workflows/` — ✅ de-duplicated 2026-05-29: the canonical copies already live in Local-Network-Hub; the redundant Claude_Vault copy (byte-identical) was archived to `exports/_archived_2026-05-29/` and removed from the vault root. TSK-0004 closed as superseded.
- `C:\Users\MarsBase\Documents\Claude_Vault\` (literal-path ghost directory) — ✅ gone.

Scan-excludes for `llm-orchestrator`/`Claude_on_Claude` are retained as defensive guards only.

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
