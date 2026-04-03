---
type: briefing
compiled: "2026-04-03T08:45:33Z"
token_budget: 8000
token_actual: 7963
scope: auto-compiled
notes_included:
  - "Dashboard.md"
  - "knowledge/KNW-0005.md"
  - "knowledge/KNW-0003.md"
  - "Vault_Health.md"
  - "Task_Board.md"
  - "README.md"
  - "tasks/TSK-0002.md"
  - "tasks/TSK-0001.md"
  - "knowledge/KNW-0004.md"
  - "_templates/weekly.md"
  - "_templates/daily.md"
  - "knowledge/KNW-0002.md"
  - "knowledge/KNW-0001.md"
notes_excluded_reason:
  - path: "_templates/task.md"
    reason: "token budget exceeded (need 113, remaining 37)"
  - path: "_templates/knowledge.md"
    reason: "token budget exceeded (need 111, remaining 37)"
  - path: "_templates/session.md"
    reason: "token budget exceeded (need 95, remaining 37)"
  - path: "_templates/decision.md"
    reason: "token budget exceeded (need 133, remaining 37)"
  - path: "sessions/SES-2026-04-02-001.md"
    reason: "token budget exceeded (need 744, remaining 37)"
---

## Vault State

- **Total notes:** 19
- **Open tasks:** 2
- **Recent decisions:** 1

## Changed Since Last Compile

**(root)/**
- [[Vault_Health.md]]
- [[Task_Board.md]]
- [[README.md]]
- [[Dashboard.md]]

**_templates/**
- [[_templates/weekly.md]]
- [[_templates/daily.md]]

**knowledge/**
- [[knowledge/KNW-0005.md]]
- [[knowledge/KNW-0004.md]]
- [[knowledge/KNW-0003.md]]
- [[knowledge/KNW-0002.md]]
- [[knowledge/KNW-0001.md]]

**tasks/**
- [[tasks/TSK-0002.md]]
- [[tasks/TSK-0001.md]]


## Key Context

### [[Dashboard.md]]

- **Score:** 0.865 (recency=0.99, delta=1.00, links=0.33, importance=1.00)
- **Tokens:** ~856

> **Quick Actions**  `BUTTON[compile-briefing]`  `BUTTON[drift-scan]`  `BUTTON[new-decision]`  `BUTTON[new-task]`  `BUTTON[quick-capture]`

### [[knowledge/KNW-0005.md]]

- **Score:** 0.725 (recency=0.64, delta=1.00, links=0.67, importance=0.50)
- **Tokens:** ~650

The drift-detector plugin continuously monitors vault integrity. "Drift" is any state where the vault's contents diverge from its intended structure or internal consistency. The plugin runs four independent scanners, each targeting a different failure mode.

### [[knowledge/KNW-0003.md]]

- **Score:** 0.725 (recency=0.64, delta=1.00, links=0.67, importance=0.50)
- **Tokens:** ~600

The context-compiler plugin produces a token-budgeted briefing (`_system/_briefing.md`) that gives an AI session the most relevant vault context within a fixed token window. It solves the core problem of cross-session continuity: each new Claude session starts with no memory, so the briefing reconst...

### [[Vault_Health.md]]

- **Score:** 0.708 (recency=0.64, delta=1.00, links=0.33, importance=0.75)
- **Tokens:** ~2368

> Comprehensive operational health metrics for the Claude Vault. > All sections are live — powered by Dataview and DataviewJS.

### [[Task_Board.md]]

- **Score:** 0.700 (recency=1.00, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~109

- [ ] [[tasks/TSK-0001|Index Force Multiplication v1 vault architecture]] - [ ] [[tasks/TSK-0002|Configure Local REST API for external agent access]]

### [[README.md]]

- **Score:** 0.670 (recency=0.68, delta=1.00, links=0.33, importance=0.50)
- **Tokens:** ~977

This is not a human notebook. It is an operational layer for AI systems — Claude Code, Claude Desktop, Claude API, and local models.

### [[tasks/TSK-0002.md]]

- **Score:** 0.667 (recency=0.67, delta=1.00, links=0.33, importance=0.50)
- **Tokens:** ~187

Configure the obsidian-local-rest-api plugin with proper authentication and test that Claude Code can read/write vault notes over HTTP. This enables any Claude instance (Code, Desktop, API) to interact with the vault without filesystem access.

### [[tasks/TSK-0001.md]]

- **Score:** 0.667 (recency=0.67, delta=1.00, links=0.33, importance=0.50)
- **Tokens:** ~181

Scan the user's main knowledge base (Force Multiplication v1, 4,351 files) and create knowledge entries documenting its folder structure, key files, organizational schema, and how it connects to the rest of the ecosystem.

### [[knowledge/KNW-0004.md]]

- **Score:** 0.658 (recency=0.64, delta=1.00, links=0.33, importance=0.50)
- **Tokens:** ~500

Every decision in the vault has a unique ID (`DEC-NNNN`) and a status field that tracks its lifecycle:

### [[_templates/weekly.md]]

- **Score:** 0.595 (recency=0.65, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~354

```dataview TABLE title, status, date FROM "decisions" WHERE type = "decision" AND date >= date("<% tp.date.now("YYYY-MM-DD", -7) %>") SORT date DESC ```

### [[_templates/daily.md]]

- **Score:** 0.594 (recency=0.65, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~181

```dataview TABLE agent, status, summary FROM "sessions" WHERE type = "session" AND date = date("<% tp.date.now("YYYY-MM-DD") %>") SORT file.ctime ASC ```

### [[knowledge/KNW-0002.md]]

- **Score:** 0.591 (recency=0.64, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~550

Notes are **machine-readable first**. Frontmatter is the primary structured data; the Markdown body provides supplementary context for human readers and for AI sessions that need deeper understanding. Every note type has a defined schema, and every automation layer reads frontmatter fields as its da...

### [[knowledge/KNW-0001.md]]

- **Score:** 0.591 (recency=0.64, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~450

Windows 11 Home, build 10.0.26300. User profile path: `C:\Users\MarsBase`. Primary documents directory: `C:\Users\MarsBase\Documents`.

## Open Tasks

- **[[tasks/TSK-0002.md|Configure Local REST API for external agent access]]** — status: open, priority: normal
- **[[tasks/TSK-0001.md|Index Force Multiplication v1 vault architecture]]** — status: open, priority: normal

## Recent Decisions

- **[[decisions/DEC-0001.md|Vault structure — flat folders over nested hierarchy]]** (2026-04-02): Shallow folders (one level) with rich frontmatter. Deep nesting makes path construction fragile — I'd need to know the full tree to create or find a note. Flat-with-tags loses the ability to scope Dataview queries by folder. One level of semantic folders gives both: folder-scoped queries AND simple paths.

## Drift Warnings

Issues detected in `_system/_drift_report.md`:

- **Critical:** 2
- **High:** 2
- **Medium:** 3
- **Low:** 2
