---
type: briefing
compiled: "2026-04-11T23:47:17Z"
token_budget: 8000
token_actual: 7993
scope: auto-compiled
notes_included:
  - "tasks/TSK-0002.md"
  - "inbox/2026-04-11.md"
  - "knowledge/KNW-0010.md"
  - "tasks/TSK-0010.md"
  - "tasks/TSK-0009.md"
  - "tasks/TSK-0008.md"
  - "tasks/TSK-0007.md"
  - "tasks/TSK-0006.md"
  - "tasks/TSK-0005.md"
  - "tasks/TSK-0004.md"
  - "sessions/daily/2024-01-26.md"
  - "Claude_on_Claude/docs/N8N-MIGRATION.md"
  - "knowledge/KNW-0011.md"
  - "knowledge/KNW-0020.md"
  - "Claude_on_Claude/openclaw-config/skills/model-router.md"
  - "Claude_on_Claude/openclaw-config/skills/vault-sync.md"
  - "inbox/2026-04-08.md"
  - "_templates/rag-question.md"
  - "13 keyboard shortcuts.md"
  - "inbox/2026-04-06.md"
  - "inbox/2026-04-05.md"
  - "inbox/2026-04-03.md"
notes_excluded_reason:
  - path: "Claude_on_Claude/docs/ARCHITECTURE.md"
    reason: "token budget exceeded (need 1755, remaining 796)"
  - path: "Claude_on_Claude/docs/HANDOFF-PROTOCOL.md"
    reason: "token budget exceeded (need 2646, remaining 796)"
  - path: "knowledge/KNW-0019.md"
    reason: "token budget exceeded (need 1500, remaining 796)"
  - path: "Claude_on_Claude/openclaw-config/MEMORY.md"
    reason: "token budget exceeded (need 314, remaining 263)"
  - path: "Claude_on_Claude/mcp-servers/openrouter-mcp/README.md"
    reason: "token budget exceeded (need 494, remaining 263)"
---

## Vault State

- **Total notes:** 66
- **Open tasks:** 9
- **Recent decisions:** 2

## Changed Since Last Compile

**inbox/**
- [[inbox/2026-04-11.md]]


## Key Context

### [[tasks/TSK-0002.md]]

- **Score:** 0.800 (recency=0.95, delta=0.94, links=0.67, importance=0.50)
- **Tokens:** ~307

Configure the obsidian-local-rest-api plugin with proper authentication and test that Claude Code can read/write vault notes over HTTP. This enables any Claude instance (Code, Desktop, API) to interact with the vault without filesystem access.

### [[inbox/2026-04-11.md]]

- **Score:** 0.767 (recency=1.00, delta=1.00, links=0.33, importance=0.50)
- **Tokens:** ~31

--- **15:25:53** — Vault opened. Session started.

### [[knowledge/KNW-0010.md]]

- **Score:** 0.734 (recency=0.95, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~1200

Mars is building a **distributed multi-agent orchestration system** across multiple AI providers, local models, and automation layers. This is not a collection of tools — it is a unified stack where each node has a defined role.

### [[tasks/TSK-0010.md]]

- **Score:** 0.734 (recency=0.95, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~400

> The workflow of the day. Every morning, the system wakes up, reads the vault, triages tasks, and prepares a briefing. This is the heartbeat.

### [[tasks/TSK-0009.md]]

- **Score:** 0.734 (recency=0.95, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~350

> 1,600+ files of accumulated human knowledge sit in FM v1. Agents can't use what they can't find. This task makes that knowledge searchable.

### [[tasks/TSK-0008.md]]

- **Score:** 0.734 (recency=0.95, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~350

> A system that can't trust its own memory is broken. This task cleans the vault so every agent reads accurate data.

### [[tasks/TSK-0007.md]]

- **Score:** 0.734 (recency=0.95, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~400

> The VPS is the spine — the central relay that n8n, OpenClaw, and remote agents attach to. Without it, everything stays local-only.

### [[tasks/TSK-0006.md]]

- **Score:** 0.734 (recency=0.95, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~450

> Local models are the bones — the structural foundation that holds everything up when the internet goes dark. This task hardens the local inference layer.

### [[tasks/TSK-0005.md]]

- **Score:** 0.734 (recency=0.95, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~400

> Obsidian is the blood of this system. Every agent reads from it, every result writes back to it. This task makes that flow reliable.

### [[tasks/TSK-0004.md]]

- **Score:** 0.733 (recency=0.95, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~935

> **DEADLINE: 2026-04-20** — n8n free trial expires. All workflows must be extracted to offline scripts.

### [[sessions/daily/2024-01-26.md]]

- **Score:** 0.733 (recency=0.95, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~180

```dataview TABLE agent, status, summary FROM "sessions" WHERE type = "session" AND date = date("2026-04-03") SORT file.ctime ASC ```

### [[Claude_on_Claude/docs/N8N-MIGRATION.md]]

- **Score:** 0.729 (recency=0.94, delta=0.93, links=0.33, importance=0.50)
- **Tokens:** ~1251

- [x] Open n8n cloud instance - [x] Export workflows as JSON (n8n-workflows-backup-[timestamp].json) - [x] Copy backup to `Claude_on_Claude/n8n-workflows/` and commit

### [[knowledge/KNW-0011.md]]

- **Score:** 0.729 (recency=0.94, delta=0.93, links=0.33, importance=0.50)
- **Tokens:** ~500

Live status of every connection point in the orchestration stack. Update this entry whenever a connection is confirmed, broken, or changed.

### [[knowledge/KNW-0020.md]]

- **Score:** 0.714 (recency=0.92, delta=0.91, links=0.33, importance=0.50)
- **Tokens:** ~450

Full specification lives in the Claude_on_Claude repo: `Claude_on_Claude/docs/HANDOFF-PROTOCOL.md`

### [[Claude_on_Claude/openclaw-config/skills/model-router.md]]

- **Score:** 0.632 (recency=0.80, delta=0.75, links=0.33, importance=0.50)
- **Tokens:** ~271

Smart model selection based on task type, urgency, and remaining free quota.

### [[Claude_on_Claude/openclaw-config/skills/vault-sync.md]]

- **Score:** 0.632 (recency=0.80, delta=0.75, links=0.33, importance=0.50)
- **Tokens:** ~262

Synchronize state between OpenClaw agent memory and Obsidian vaults via REST API.

### [[inbox/2026-04-08.md]]

- **Score:** 0.562 (recency=0.70, delta=0.62, links=0.33, importance=0.50)
- **Tokens:** ~31

--- **22:16:00** — Vault opened. Session started.

### [[_templates/rag-question.md]]

- **Score:** 0.556 (recency=0.69, delta=0.61, links=0.33, importance=0.50)
- **Tokens:** ~69

<% tp.file.cursor() %>

### [[13 keyboard shortcuts.md]]

- **Score:** 0.542 (recency=0.67, delta=0.58, links=0.33, importance=0.50)
- **Tokens:** ~50

Placeholder note created from template. Originally had duplicate ID KNW-0006 (conflict with Force Multiplication v1 entry). Reassigned to KNW-0012. Needs content or user decision to delete.

### [[inbox/2026-04-06.md]]

- **Score:** 0.354 (recency=0.39, delta=0.23, links=0.33, importance=0.50)
- **Tokens:** ~18

--- **06:13:45** — Vault opened. Session started.

### [[inbox/2026-04-05.md]]

- **Score:** 0.334 (recency=0.37, delta=0.19, links=0.33, importance=0.50)
- **Tokens:** ~44

--- **22:44:36** — Vault opened. Session started.

### [[inbox/2026-04-03.md]]

- **Score:** 0.273 (recency=0.13, delta=0.00, links=0.67, importance=0.50)
- **Tokens:** ~44

--- **15:30:49** — Vault opened. Session started.

## Open Tasks

- **[[tasks/TSK-0010.md|Daily Workflow Nerve — Automated Vault Briefing + Task Triage]]** — status: open, priority: normal
- **[[tasks/TSK-0009.md|Force Multiplication v1 — RAG Index for Agent Context]]** — status: open, priority: normal
- **[[tasks/TSK-0008.md|Vault Health Sweep — Fix Drift, Schema, Stale Refs]]** — status: open, priority: normal
- **[[tasks/TSK-0006.md|Local LLM Bones — Ollama Service + Model Selection + Always-On Fallback]]** — status: open, priority: high
- **[[tasks/TSK-0005.md|Obsidian Blood Flow — Vault REST API Pipeline for All Agents]]** — status: open, priority: high
- **[[tasks/TSK-0004.md|T-13 Days n8n Extraction and Hardening Protocol]]** — status: in_progress, priority: critical
- **[[tasks/TSK-0003.md|agentA-Z Keyboard — Android AI keyboard orchestration system]]** — status: in_progress, priority: normal
- **[[tasks/TSK-0002.md|Configure Local REST API for external agent access]]** — status: open, priority: normal
- **[[tasks/TSK-0001.md|Index Force Multiplication v1 vault architecture]]** — status: open, priority: normal

## Recent Decisions

- **[[decisions/DEC-0002.md|agentA-Z keyboard — FlorisBoard as IME base over AnySoftKeyboard and from-scratch]]** (2026-04-06): FlorisBoard is Kotlin-native, has an existing Addons Store + extension system, spell-checker hooks we can repurpose for AI injection, and JSON-based theme/layout config that maps directly to our skills.json approach. Active development community. Apache-2.0 license allows unrestricted forking.
- **[[decisions/DEC-0001.md|Vault structure — flat folders over nested hierarchy]]** (2026-04-02): Shallow folders (one level) with rich frontmatter. Deep nesting makes path construction fragile — I'd need to know the full tree to create or find a note. Flat-with-tags loses the ability to scope Dataview queries by folder. One level of semantic folders gives both: folder-scoped queries AND simple paths.

## Drift Warnings

Issues detected in `_system/_drift_report.md`:

- **Critical:** 2
- **High:** 3
- **Medium:** 3
- **Low:** 2
