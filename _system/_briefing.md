---
type: briefing
compiled: "2026-05-17T18:48:07Z"
token_budget: 8000
token_actual: 7989
scope: auto-compiled
notes_included:
  - "inbox/2026-05-17.md"
  - "sessions/SES-2026-05-04-001.md"
  - "memory/glossary.md"
  - "memory/context/api-budgets.md"
  - "inbox/docs-audit-2026-05-03.md"
  - "inbox/2026-04-26.md"
  - "decisions/DEC-0003.md"
  - "tasks/TSK-0003.md"
  - "tasks/TSK-0001.md"
  - "knowledge/KNW-0022.md"
  - "tasks/TSK-0007.md"
  - "tasks/TSK-0009.md"
  - "sessions/daily/2026-04-03.md"
  - "inbox/2026-04-20.md"
  - "tasks/TSK-0002.md"
  - "inbox/2026-04-15.md"
  - "inbox/2026-04-14.md"
  - "inbox/2026-04-11.md"
  - "inbox/2026-04-03.md"
notes_excluded_reason:
  - path: "sessions/SES-2026-04-21-copilot-cli-backend-hang.md"
    reason: "token budget exceeded (need 2400, remaining 2291)"
  - path: "sessions/SES-2026-04-17-001.md"
    reason: "token budget exceeded (need 900, remaining 641)"
  - path: "sessions/SES-2026-04-19-001.md"
    reason: "token budget exceeded (need 1200, remaining 442)"
  - path: "CLAUDE.md"
    reason: "token budget exceeded (need 1782, remaining 104)"
  - path: "Dashboard.md"
    reason: "token budget exceeded (need 856, remaining 104)"
---

## Vault State

- **Total notes:** 65
- **Open tasks:** 6
- **Recent decisions:** 3

## Changed Since Last Compile

**inbox/**
- [[inbox/2026-05-17.md]]
- [[inbox/docs-audit-2026-05-03.md]]
- [[inbox/2026-04-26.md]]

**memory/**
- [[memory/glossary.md]]

**memory/context/**
- [[memory/context/api-budgets.md]]

**sessions/**
- [[sessions/SES-2026-05-04-001.md]]


## Key Context

### [[inbox/2026-05-17.md]]

- **Score:** 0.700 (recency=1.00, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~18

--- **11:48:06** — Vault opened. Session started.

### [[sessions/SES-2026-05-04-001.md]]

- **Score:** 0.612 (recency=0.71, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~450

Vault-sync skill creation, test evaluation, drift fixes, memory enrichment

### [[memory/glossary.md]]

- **Score:** 0.612 (recency=0.71, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~738

Workplace shorthand, acronyms, API services, and internal language.

### [[memory/context/api-budgets.md]]

- **Score:** 0.612 (recency=0.71, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~828

Last updated: 2026-05-04 (vault-sync session — staleness sweep)

### [[inbox/docs-audit-2026-05-03.md]]

- **Score:** 0.607 (recency=0.69, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~1882

**Date:** 2026-05-03 **Scope:** Cross-analysis of all vaults against GitHub repository best-practice standards **Auditor:** Claude (Sonnet 4.6)

### [[inbox/2026-04-26.md]]

- **Score:** 0.602 (recency=0.54, delta=1.00, links=0.20, importance=0.50)
- **Tokens:** ~18

--- **21:29:58** — Vault opened. Session started.

### [[decisions/DEC-0003.md]]

- **Score:** 0.454 (recency=0.40, delta=0.11, links=1.00, importance=0.50)
- **Tokens:** ~650

The vault's own docs (CLAUDE.md, vault_config.yaml, MAD_MAX_STATUS.md, Claude_on_Claude/docs/ARCHITECTURE.md, and ~10 knowledge entries) described a 3-vault ecosystem:

### [[tasks/TSK-0003.md]]

- **Score:** 0.374 (recency=0.40, delta=0.11, links=0.60, importance=0.50)
- **Tokens:** ~709

> **ICEBOXED 2026-04-19** — per Mars, the keyboard project gets its own non-vault folder at `Documents\agentA-Z\` with its own repo. It is explicitly NOT part of the 4-vault system (see [[decisions/DEC-0003]]). This task stays here as a pointer; the real work resumes when the project folder is scaff...

### [[tasks/TSK-0001.md]]

- **Score:** 0.334 (recency=0.40, delta=0.11, links=0.40, importance=0.50)
- **Tokens:** ~416

> **RETARGETED 2026-04-19** — per [[decisions/DEC-0003]], Force Multiplication v1 is no longer part of the active system. This task shifts from "index FM v1" to "scaffold RAG_Vault and migrate structured knowledge into it." Mars to review and confirm scope before work resumes.

### [[knowledge/KNW-0022.md]]

- **Score:** 0.295 (recency=0.38, delta=0.00, links=0.40, importance=0.50)
- **Tokens:** ~900

Mars flagged conflict in repos, drift in Claude Code WSL work, and possible pushes to a ghost repo. Direct inspection on 2026-04-19 confirms:

### [[tasks/TSK-0007.md]]

- **Score:** 0.294 (recency=0.40, delta=0.11, links=0.20, importance=0.50)
- **Tokens:** ~400

> The VPS is the spine — the central relay that n8n, OpenClaw, and remote agents attach to. Without it, everything stays local-only.

### [[tasks/TSK-0009.md]]

- **Score:** 0.294 (recency=0.40, delta=0.11, links=0.20, importance=0.50)
- **Tokens:** ~350

> **RETARGETED 2026-04-19** — per [[decisions/DEC-0003]], FM v1 is out of the system. This task becomes: wire the RAG pipeline against RAG_Vault (scaffolded in TSK-0001), not FM v1. Scope needs confirmation by Mars before resuming.

### [[sessions/daily/2026-04-03.md]]

- **Score:** 0.294 (recency=0.40, delta=0.11, links=0.20, importance=0.50)
- **Tokens:** ~181

```dataview TABLE agent, status, summary FROM "sessions" WHERE type = "session" AND date = date("2026-04-03") SORT file.ctime ASC ```

### [[inbox/2026-04-20.md]]

- **Score:** 0.287 (recency=0.40, delta=0.09, links=0.20, importance=0.50)
- **Tokens:** ~18

--- **12:49:42** — Vault opened. Session started.

### [[tasks/TSK-0002.md]]

- **Score:** 0.237 (recency=0.19, delta=0.00, links=0.40, importance=0.50)
- **Tokens:** ~307

Configure the obsidian-local-rest-api plugin with proper authentication and test that Claude Code can read/write vault notes over HTTP. This enables any Claude instance (Code, Desktop, API) to interact with the vault without filesystem access.

### [[inbox/2026-04-15.md]]

- **Score:** 0.228 (recency=0.29, delta=0.00, links=0.20, importance=0.50)
- **Tokens:** ~31

--- **09:36:16** — Vault opened. Session started.

### [[inbox/2026-04-14.md]]

- **Score:** 0.176 (recency=0.25, delta=0.00, links=0.00, importance=0.50)
- **Tokens:** ~18

--- **01:29:29** — Vault opened. Session started.

### [[inbox/2026-04-11.md]]

- **Score:** 0.160 (recency=0.20, delta=0.00, links=0.00, importance=0.50)
- **Tokens:** ~31

--- **15:25:53** — Vault opened. Session started.

### [[inbox/2026-04-03.md]]

- **Score:** 0.148 (recency=0.03, delta=0.00, links=0.20, importance=0.50)
- **Tokens:** ~44

--- **15:30:49** — Vault opened. Session started.

## Open Tasks

- **[[tasks/TSK-0010.md|Daily Workflow Nerve — Automated Vault Briefing + Task Triage]]** — status: open, priority: normal
- **[[tasks/TSK-0008.md|Vault Health Sweep — Fix Drift, Schema, Stale Refs]]** — status: open, priority: normal
- **[[tasks/TSK-0006.md|Local LLM Bones — Ollama Service + Model Selection + Always-On Fallback]]** — status: open, priority: high
- **[[tasks/TSK-0005.md|Obsidian Blood Flow — Vault REST API Pipeline for All Agents]]** — status: open, priority: high
- **[[tasks/TSK-0004.md|T-13 Days n8n Extraction and Hardening Protocol]]** — status: in_progress, priority: critical
- **[[tasks/TSK-0002.md|Configure Local REST API for external agent access]]** — status: open, priority: normal

## Recent Decisions

- **[[decisions/DEC-0003.md|4-vault architecture correction — Command_Vault + Local-Network-Hub + Claude_Vault + RAG_Vault]]** (2026-04-19): Each vault gets one role: Command_Vault monitors, Local-Network-Hub orchestrates, Claude_Vault is AI ops, RAG_Vault is retrieval. Removes FM v1 dependency. Enables clean repo-per-vault.
- **[[decisions/DEC-0002.md|agentA-Z keyboard — FlorisBoard as IME base over AnySoftKeyboard and from-scratch]]** (2026-04-06): FlorisBoard is Kotlin-native, has an existing Addons Store + extension system, spell-checker hooks we can repurpose for AI injection, and JSON-based theme/layout config that maps directly to our skills.json approach. Active development community. Apache-2.0 license allows unrestricted forking.
- **[[decisions/DEC-0001.md|Vault structure — flat folders over nested hierarchy]]** (2026-04-02): Shallow folders (one level) with rich frontmatter. Deep nesting makes path construction fragile — I'd need to know the full tree to create or find a note. Flat-with-tags loses the ability to scope Dataview queries by folder. One level of semantic folders gives both: folder-scoped queries AND simple paths.

## Drift Warnings

Issues detected in `_system/_drift_report.md`:

- **Critical:** 2
- **High:** 3
- **Medium:** 3
- **Low:** 3
