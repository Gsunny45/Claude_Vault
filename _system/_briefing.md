---
type: briefing
compiled: "2026-04-06T05:44:37Z"
token_budget: 8000
token_actual: 7946
scope: auto-compiled
notes_included:
  - "inbox/2026-04-05.md"
  - "inbox/2026-04-04.md"
  - "inbox/2026-04-03.md"
  - "CLAUDE.md"
  - "knowledge/KNW-0007.md"
  - "knowledge/KNW-0006.md"
  - "knowledge/KNW-0005.md"
  - "knowledge/KNW-0003.md"
  - "Vault_Health.md"
  - "Dashboard.md"
  - "tasks/TSK-0002.md"
  - "tasks/TSK-0001.md"
  - "_templates/task.md"
  - "_templates/knowledge.md"
  - "_templates/decision.md"
  - "_templates/startup.md"
  - "sessions/daily/2024-01-26.md"
  - "_templates/Preloaded Classes/202401211512 Notebook CSS Classes.md"
  - "_templates/Preloaded Classes/202403091325 General Tweaks CSS Classes.md"
notes_excluded_reason:
  - path: "knowledge/KNW-0004.md"
    reason: "token budget exceeded (need 500, remaining 54)"
  - path: "decisions/DEC-0001.md"
    reason: "token budget exceeded (need 180, remaining 54)"
  - path: "_templates/daily.md"
    reason: "token budget exceeded (need 222, remaining 54)"
  - path: "13 keyboard shortcuts.md"
    reason: "token budget exceeded (need 449, remaining 54)"
  - path: "Task_Board.md"
    reason: "token budget exceeded (need 109, remaining 54)"
---

## Vault State

- **Total notes:** 30
- **Open tasks:** 2
- **Recent decisions:** 1

## Changed Since Last Compile

**inbox/**
- [[inbox/2026-04-05.md]]


## Key Context

### [[inbox/2026-04-05.md]]

- **Score:** 0.700 (recency=1.00, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~18

--- **22:44:36** — Vault opened. Session started.

### [[inbox/2026-04-04.md]]

- **Score:** 0.627 (recency=0.54, delta=1.00, links=0.33, importance=0.50)
- **Tokens:** ~31

--- **01:18:26** — Vault opened. Session started.

### [[inbox/2026-04-03.md]]

- **Score:** 0.621 (recency=0.37, delta=0.92, links=0.67, importance=0.50)
- **Tokens:** ~44

--- **15:30:49** — Vault opened. Session started.

### [[CLAUDE.md]]

- **Score:** 0.568 (recency=0.40, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~1057

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

### [[knowledge/KNW-0007.md]]

- **Score:** 0.567 (recency=0.40, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~650

Local-Network-Hub is the user's production AI workflow coordination system at `C:\Users\MarsBase\Documents\Local-Network-Hub`. It's an Obsidian vault designed as a persistent workspace where humans and AI agents collaborate through standardized note structure, task queue, session logging, and handof...

### [[knowledge/KNW-0006.md]]

- **Score:** 0.567 (recency=0.40, delta=0.94, links=0.33, importance=0.50)
- **Tokens:** ~500

Force Multiplication v1 is the user's main knowledge base — 1,600+ files at `C:\Users\MarsBase\Documents\Force Multiplication v1`. It's a multi-purpose personal knowledge management system undergoing a major reorganization (25% complete).

### [[knowledge/KNW-0005.md]]

- **Score:** 0.555 (recency=0.07, delta=0.78, links=1.00, importance=0.50)
- **Tokens:** ~650

The drift-detector plugin continuously monitors vault integrity. "Drift" is any state where the vault's contents diverge from its intended structure or internal consistency. The plugin runs four independent scanners, each targeting a different failure mode.

### [[knowledge/KNW-0003.md]]

- **Score:** 0.555 (recency=0.07, delta=0.78, links=1.00, importance=0.50)
- **Tokens:** ~600

The context-compiler plugin produces a token-budgeted briefing (`_system/_briefing.md`) that gives an AI session the most relevant vault context within a fixed token window. It solves the core problem of cross-session continuity: each new Claude session starts with no memory, so the briefing reconst...

### [[Vault_Health.md]]

- **Score:** 0.538 (recency=0.07, delta=0.78, links=0.67, importance=0.75)
- **Tokens:** ~2368

> Comprehensive operational health metrics for the Claude Vault. > All sections are live — powered by Dataview and DataviewJS.

### [[Dashboard.md]]

- **Score:** 0.537 (recency=0.10, delta=0.80, links=0.33, importance=1.00)
- **Tokens:** ~856

> **Quick Actions**  `BUTTON[compile-briefing]`  `BUTTON[drift-scan]`  `BUTTON[new-decision]`  `BUTTON[new-task]`  `BUTTON[quick-capture]`

### [[tasks/TSK-0002.md]]

- **Score:** 0.489 (recency=0.07, delta=0.78, links=0.67, importance=0.50)
- **Tokens:** ~187

Configure the obsidian-local-rest-api plugin with proper authentication and test that Claude Code can read/write vault notes over HTTP. This enables any Claude instance (Code, Desktop, API) to interact with the vault without filesystem access.

### [[tasks/TSK-0001.md]]

- **Score:** 0.489 (recency=0.07, delta=0.78, links=0.67, importance=0.50)
- **Tokens:** ~181

Scan the user's main knowledge base (Force Multiplication v1, 4,351 files) and create knowledge entries documenting its folder structure, key files, organizational schema, and how it connects to the rest of the ecosystem.

### [[_templates/task.md]]

- **Score:** 0.469 (recency=0.17, delta=0.83, links=0.33, importance=0.50)
- **Tokens:** ~76

<% tp.file.cursor(2) %>

### [[_templates/knowledge.md]]

- **Score:** 0.469 (recency=0.17, delta=0.83, links=0.33, importance=0.50)
- **Tokens:** ~73

<% tp.file.cursor(3) %>

### [[_templates/decision.md]]

- **Score:** 0.468 (recency=0.17, delta=0.83, links=0.33, importance=0.50)
- **Tokens:** ~95

<% tp.file.cursor(5) %>

### [[_templates/startup.md]]

- **Score:** 0.468 (recency=0.17, delta=0.83, links=0.33, importance=0.50)
- **Tokens:** ~204

<%* // Startup template — runs on vault open // Appends a session marker to today's inbox file

### [[sessions/daily/2024-01-26.md]]

- **Score:** 0.457 (recency=0.15, delta=0.82, links=0.33, importance=0.50)
- **Tokens:** ~164

```dataview TABLE agent, status, summary FROM "sessions" WHERE type = "session" AND date = date("2026-04-03") SORT file.ctime ASC ```

### [[_templates/Preloaded Classes/202401211512 Notebook CSS Classes.md]]

- **Score:** 0.457 (recency=0.15, delta=0.82, links=0.33, importance=0.50)
- **Tokens:** ~138

<mark style="background:#d3f8b6"><div style="background-color=black;color:white"></mark> <mark style="background:#d3f8b6"><i>This page is only for keeping CSS classes ready for autocomplete.</i></mark> <mark style="background:#d3f8b6"></div></mark>

### [[_templates/Preloaded Classes/202403091325 General Tweaks CSS Classes.md]]

- **Score:** 0.457 (recency=0.15, delta=0.82, links=0.33, importance=0.50)
- **Tokens:** ~54

<div style="background-color=black;color:white"> <i>This page is only for keeping CSS classes ready for autocomplete.</i> </div>

## Open Tasks

- **[[tasks/TSK-0002.md|Configure Local REST API for external agent access]]** — status: open, priority: normal
- **[[tasks/TSK-0001.md|Index Force Multiplication v1 vault architecture]]** — status: open, priority: normal

## Recent Decisions

- **[[decisions/DEC-0001.md|Vault structure — flat folders over nested hierarchy]]** (2026-04-02): Shallow folders (one level) with rich frontmatter. Deep nesting makes path construction fragile — I'd need to know the full tree to create or find a note. Flat-with-tags loses the ability to scope Dataview queries by folder. One level of semantic folders gives both: folder-scoped queries AND simple paths.

## Drift Warnings

Issues detected in `_system/_drift_report.md`:

- **Critical:** 3
- **High:** 3
- **Medium:** 3
- **Low:** 2
