---
type: briefing
compiled: "2026-04-04T04:51:08Z"
token_budget: 8000
token_actual: 7947
scope: auto-compiled
notes_included:
  - "inbox/2026-04-03.md"
  - "Dashboard.md"
  - "knowledge/KNW-0005.md"
  - "knowledge/KNW-0003.md"
  - "Vault_Health.md"
  - "_templates/task.md"
  - "_templates/knowledge.md"
  - "_templates/decision.md"
  - "_templates/startup.md"
  - "sessions/daily/2024-01-26.md"
  - "_templates/Preloaded Classes/202401211512 Notebook CSS Classes.md"
  - "_templates/Preloaded Classes/202403091325 General Tweaks CSS Classes.md"
  - "_templates/daily.md"
  - "tasks/TSK-0002.md"
  - "tasks/TSK-0001.md"
  - "knowledge/KNW-0004.md"
  - "13 keyboard shortcuts.md"
  - "Task_Board.md"
  - "README.md"
notes_excluded_reason:
  - path: "decisions/DEC-0001.md"
    reason: "token budget exceeded (need 180, remaining 53)"
  - path: "_templates/weekly.md"
    reason: "token budget exceeded (need 354, remaining 53)"
  - path: "knowledge/KNW-0002.md"
    reason: "token budget exceeded (need 550, remaining 53)"
  - path: "knowledge/KNW-0001.md"
    reason: "token budget exceeded (need 450, remaining 53)"
  - path: "_templates/session.md"
    reason: "token budget exceeded (need 95, remaining 53)"
---

## Vault State

- **Total notes:** 25
- **Open tasks:** 2
- **Recent decisions:** 1

## Changed Since Last Compile

**inbox/**
- [[inbox/2026-04-03.md]]


## Key Context

### [[inbox/2026-04-03.md]]

- **Score:** 0.833 (recency=1.00, delta=1.00, links=0.67, importance=0.50)
- **Tokens:** ~44

--- **15:30:49** — Vault opened. Session started.

### [[Dashboard.md]]

- **Score:** 0.614 (recency=0.28, delta=0.88, links=0.33, importance=1.00)
- **Tokens:** ~856

> **Quick Actions**  `BUTTON[compile-briefing]`  `BUTTON[drift-scan]`  `BUTTON[new-decision]`  `BUTTON[new-task]`  `BUTTON[quick-capture]`

### [[knowledge/KNW-0005.md]]

- **Score:** 0.613 (recency=0.18, delta=0.87, links=1.00, importance=0.50)
- **Tokens:** ~650

The drift-detector plugin continuously monitors vault integrity. "Drift" is any state where the vault's contents diverge from its intended structure or internal consistency. The plugin runs four independent scanners, each targeting a different failure mode.

### [[knowledge/KNW-0003.md]]

- **Score:** 0.613 (recency=0.18, delta=0.87, links=1.00, importance=0.50)
- **Tokens:** ~600

The context-compiler plugin produces a token-budgeted briefing (`_system/_briefing.md`) that gives an AI session the most relevant vault context within a fixed token window. It solves the core problem of cross-session continuity: each new Claude session starts with no memory, so the briefing reconst...

### [[Vault_Health.md]]

- **Score:** 0.596 (recency=0.18, delta=0.87, links=0.67, importance=0.75)
- **Tokens:** ~2368

> Comprehensive operational health metrics for the Claude Vault. > All sections are live — powered by Dataview and DataviewJS.

### [[_templates/task.md]]

- **Score:** 0.583 (recency=0.47, delta=0.92, links=0.33, importance=0.50)
- **Tokens:** ~76

<% tp.file.cursor(2) %>

### [[_templates/knowledge.md]]

- **Score:** 0.582 (recency=0.47, delta=0.92, links=0.33, importance=0.50)
- **Tokens:** ~73

<% tp.file.cursor(3) %>

### [[_templates/decision.md]]

- **Score:** 0.582 (recency=0.47, delta=0.92, links=0.33, importance=0.50)
- **Tokens:** ~95

<% tp.file.cursor(5) %>

### [[_templates/startup.md]]

- **Score:** 0.581 (recency=0.47, delta=0.91, links=0.33, importance=0.50)
- **Tokens:** ~204

<%* // Startup template — runs on vault open // Appends a session marker to today's inbox file

### [[sessions/daily/2024-01-26.md]]

- **Score:** 0.557 (recency=0.40, delta=0.90, links=0.33, importance=0.50)
- **Tokens:** ~164

```dataview TABLE agent, status, summary FROM "sessions" WHERE type = "session" AND date = date("2026-04-03") SORT file.ctime ASC ```

### [[_templates/Preloaded Classes/202401211512 Notebook CSS Classes.md]]

- **Score:** 0.557 (recency=0.40, delta=0.90, links=0.33, importance=0.50)
- **Tokens:** ~138

<mark style="background:#d3f8b6"><div style="background-color=black;color:white"></mark> <mark style="background:#d3f8b6"><i>This page is only for keeping CSS classes ready for autocomplete.</i></mark> <mark style="background:#d3f8b6"></div></mark>

### [[_templates/Preloaded Classes/202403091325 General Tweaks CSS Classes.md]]

- **Score:** 0.557 (recency=0.40, delta=0.90, links=0.33, importance=0.50)
- **Tokens:** ~54

<div style="background-color=black;color:white"> <i>This page is only for keeping CSS classes ready for autocomplete.</i> </div>

### [[_templates/daily.md]]

- **Score:** 0.550 (recency=0.38, delta=0.90, links=0.33, importance=0.50)
- **Tokens:** ~222

```dataview TABLE agent, status, summary FROM "sessions" WHERE type = "session" AND date = date("<% tp.date.now("YYYY-MM-DD") %>") SORT file.ctime ASC ```

### [[tasks/TSK-0002.md]]

- **Score:** 0.549 (recency=0.19, delta=0.87, links=0.67, importance=0.50)
- **Tokens:** ~187

Configure the obsidian-local-rest-api plugin with proper authentication and test that Claude Code can read/write vault notes over HTTP. This enables any Claude instance (Code, Desktop, API) to interact with the vault without filesystem access.

### [[tasks/TSK-0001.md]]

- **Score:** 0.549 (recency=0.19, delta=0.87, links=0.67, importance=0.50)
- **Tokens:** ~181

Scan the user's main knowledge base (Force Multiplication v1, 4,351 files) and create knowledge entries documenting its folder structure, key files, organizational schema, and how it connects to the rest of the ecosystem.

### [[knowledge/KNW-0004.md]]

- **Score:** 0.546 (recency=0.18, delta=0.87, links=0.67, importance=0.50)
- **Tokens:** ~500

Every decision in the vault has a unique ID (`DEC-NNNN`) and a status field that tracks its lifecycle:

### [[13 keyboard shortcuts.md]]

- **Score:** 0.541 (recency=0.35, delta=0.90, links=0.33, importance=0.50)
- **Tokens:** ~449

<% tp.file.cursor(3) %>

### [[Task_Board.md]]

- **Score:** 0.515 (recency=0.28, delta=0.88, links=0.33, importance=0.50)
- **Tokens:** ~109

- [ ] [[tasks/TSK-0001|Index Force Multiplication v1 vault architecture]] - [ ] [[tasks/TSK-0002|Configure Local REST API for external agent access]]

### [[README.md]]

- **Score:** 0.484 (recency=0.19, delta=0.87, links=0.33, importance=0.50)
- **Tokens:** ~977

This is not a human notebook. It is an operational layer for AI systems — Claude Code, Claude Desktop, Claude API, and local models.

## Open Tasks

- **[[tasks/TSK-0002.md|Configure Local REST API for external agent access]]** — status: open, priority: normal
- **[[tasks/TSK-0001.md|Index Force Multiplication v1 vault architecture]]** — status: open, priority: normal

## Recent Decisions

- **[[decisions/DEC-0001.md|Vault structure — flat folders over nested hierarchy]]** (2026-04-02): Shallow folders (one level) with rich frontmatter. Deep nesting makes path construction fragile — I'd need to know the full tree to create or find a note. Flat-with-tags loses the ability to scope Dataview queries by folder. One level of semantic folders gives both: folder-scoped queries AND simple paths.

## Drift Warnings

Issues detected in `_system/_drift_report.md`:

- **Critical:** 2
- **High:** 3
- **Medium:** 3
- **Low:** 2
