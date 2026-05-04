---
type: briefing
compiled: "2026-04-27T04:29:59Z"
token_budget: 8000
token_actual: 7992
scope: auto-compiled
notes_included:
  - "decisions/DEC-0003.md"
  - "tasks/TSK-0003.md"
  - "tasks/TSK-0001.md"
  - "inbox/2026-04-26.md"
  - "tasks/TSK-0009.md"
  - "sessions/SES-2026-04-17-001.md"
  - "knowledge/KNW-0022.md"
  - "inbox/2026-04-20.md"
  - "sessions/SES-2026-04-19-001.md"
  - "sessions/SES-2026-04-21-copilot-cli-backend-hang.md"
  - "tasks/TSK-0007.md"
  - "inbox/2026-04-15.md"
notes_excluded_reason:
  - path: "memory/context/api-budgets.md"
    reason: "token budget exceeded (need 782, remaining 439)"
  - path: "sessions/daily/2026-04-03.md"
    reason: "token budget exceeded (need 181, remaining 39)"
  - path: "CLAUDE.md"
    reason: "token budget exceeded (need 1782, remaining 39)"
  - path: "knowledge/KNW-0011.md"
    reason: "token budget exceeded (need 500, remaining 39)"
  - path: "MAD_MAX_STATUS.md"
    reason: "token budget exceeded (need 1868, remaining 39)"
---

## Vault State

- **Total notes:** 62
- **Open tasks:** 6
- **Recent decisions:** 3

## Changed Since Last Compile

**decisions/**
- [[decisions/DEC-0003.md]]

**inbox/**
- [[inbox/2026-04-26.md]]

**sessions/**
- [[sessions/SES-2026-04-21-copilot-cli-backend-hang.md]]
- [[sessions/SES-2026-04-17-001.md]]

**sessions/daily/**
- [[sessions/daily/2026-04-03.md]]

**tasks/**
- [[tasks/TSK-0009.md]]
- [[tasks/TSK-0007.md]]
- [[tasks/TSK-0003.md]]
- [[tasks/TSK-0001.md]]


## Key Context

### [[decisions/DEC-0003.md]]

- **Score:** 0.823 (recency=0.74, delta=1.00, links=1.00, importance=0.50)
- **Tokens:** ~650

The vault's own docs (CLAUDE.md, vault_config.yaml, MAD_MAX_STATUS.md, Claude_on_Claude/docs/ARCHITECTURE.md, and ~10 knowledge entries) described a 3-vault ecosystem:

### [[tasks/TSK-0003.md]]

- **Score:** 0.743 (recency=0.74, delta=1.00, links=0.60, importance=0.50)
- **Tokens:** ~709

> **ICEBOXED 2026-04-19** — per Mars, the keyboard project gets its own non-vault folder at `Documents\agentA-Z\` with its own repo. It is explicitly NOT part of the 4-vault system (see [[decisions/DEC-0003]]). This task stays here as a pointer; the real work resumes when the project folder is scaff...

### [[tasks/TSK-0001.md]]

- **Score:** 0.703 (recency=0.74, delta=1.00, links=0.40, importance=0.50)
- **Tokens:** ~416

> **RETARGETED 2026-04-19** — per [[decisions/DEC-0003]], Force Multiplication v1 is no longer part of the active system. This task shifts from "index FM v1" to "scaffold RAG_Vault and migrate structured knowledge into it." Mars to review and confirm scope before work resumes.

### [[inbox/2026-04-26.md]]

- **Score:** 0.700 (recency=1.00, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~18

--- **21:29:58** — Vault opened. Session started.

### [[tasks/TSK-0009.md]]

- **Score:** 0.663 (recency=0.74, delta=1.00, links=0.20, importance=0.50)
- **Tokens:** ~350

> **RETARGETED 2026-04-19** — per [[decisions/DEC-0003]], FM v1 is out of the system. This task becomes: wire the RAG pipeline against RAG_Vault (scaffolded in TSK-0001), not FM v1. Scope needs confirmation by Mars before resuming.

### [[sessions/SES-2026-04-17-001.md]]

- **Score:** 0.663 (recency=0.74, delta=1.00, links=0.20, importance=0.50)
- **Tokens:** ~900

- **Diagnosed high baseline RAM (9GB+ used)** - Fixed root cause 1: `.wslconfig memory=9GB` → changed to `memory=4GB`, swap 4GB → 2GB - Fixed root cause 2: Docker Desktop was in Windows startup registry → REMOVED - `HKCU\Software\Microsoft\Windows\CurrentVersion\Run\Docker Desktop` deleted - Was sil...

### [[knowledge/KNW-0022.md]]

- **Score:** 0.662 (recency=0.71, delta=0.90, links=0.40, importance=0.50)
- **Tokens:** ~900

Mars flagged conflict in repos, drift in Claude Code WSL work, and possible pushes to a ghost repo. Direct inspection on 2026-04-19 confirms:

### [[inbox/2026-04-20.md]]

- **Score:** 0.661 (recency=0.74, delta=1.00, links=0.20, importance=0.50)
- **Tokens:** ~18

--- **12:49:42** — Vault opened. Session started.

### [[sessions/SES-2026-04-19-001.md]]

- **Score:** 0.629 (recency=0.71, delta=0.92, links=0.20, importance=0.50)
- **Tokens:** ~1200

User (Mars) in emotional distress. Days of work on vault system feel collapsed. Architecture had been wrong in vault docs — missing Command_Vault, RAG_Vault, and Gemini_Vault at various points. Hostinger VPS blocked on SSH (provider wanting more money). n8n cloud trial expires 2026-04-20 (tomorrow)....

### [[sessions/SES-2026-04-21-copilot-cli-backend-hang.md]]

- **Score:** 0.628 (recency=0.76, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~2400

Tested GitHub Copilot CLI v1.0.34 in PowerShell 7. Identified root cause of indefinite hangs: **MCP client connects successfully to GitHub's Copilot API, but model inference requests never complete.** Auth is working (logs show "Welcome Gsunny45!"), but actual command execution hangs waiting for AI ...

### [[tasks/TSK-0007.md]]

- **Score:** 0.623 (recency=0.74, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~400

> The VPS is the spine — the central relay that n8n, OpenClaw, and remote agents attach to. Without it, everything stays local-only.

### [[inbox/2026-04-15.md]]

- **Score:** 0.402 (recency=0.54, delta=0.33, links=0.20, importance=0.50)
- **Tokens:** ~31

--- **09:36:16** — Vault opened. Session started.

## Open Tasks

- **[[tasks/TSK-0010.md|Daily Workflow Nerve — Automated Vault Briefing + Task Triage]]** — status: open, priority: normal
- **[[tasks/TSK-0008.md|Vault Health Sweep — Fix Drift, Schema, Stale Refs]]** — status: open, priority: normal
- **[[tasks/TSK-0002.md|Configure Local REST API for external agent access]]** — status: open, priority: normal
- **[[tasks/TSK-0006.md|Local LLM Bones — Ollama Service + Model Selection + Always-On Fallback]]** — status: open, priority: high
- **[[tasks/TSK-0004.md|T-13 Days n8n Extraction and Hardening Protocol]]** — status: in_progress, priority: critical
- **[[tasks/TSK-0005.md|Obsidian Blood Flow — Vault REST API Pipeline for All Agents]]** — status: open, priority: high

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
