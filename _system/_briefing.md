---
type: briefing
compiled: "2026-04-03T01:25:05Z"
token_budget: 8000
token_actual: 2577
scope: auto-compiled
notes_included:
  - "README.md"
  - "sessions/SES-2026-04-02-001.md"
  - "Dashboard.md"
  - "_templates/task.md"
  - "_templates/knowledge.md"
  - "_templates/session.md"
  - "_templates/decision.md"
  - "decisions/DEC-0001.md"
notes_excluded_reason:
---

## Vault State

- **Total notes:** 8
- **Open tasks:** 0
- **Recent decisions:** 1

## Changed Since Last Compile

**(root)/**
- [[README.md]]
- [[Dashboard.md]]

**_templates/**
- [[_templates/task.md]]
- [[_templates/session.md]]
- [[_templates/knowledge.md]]
- [[_templates/decision.md]]


## Key Context

### [[README.md]]

- **Score:** 0.900 (recency=1.00, delta=1.00, links=1.00, importance=0.50)
- **Tokens:** ~745

This is not a human notebook. It is an operational layer for AI systems — Claude Code, Claude Desktop, Claude API, and local models.

### [[sessions/SES-2026-04-02-001.md]]

- **Score:** 0.691 (recency=0.31, delta=1.00, links=1.00, importance=0.50)
- **Tokens:** ~744

Vault initialization. Built three custom Obsidian plugins from scratch: context-compiler (805 lines), decision-ledger (952 lines), drift-detector (1001 lines). Total: 2,758 lines of plugin code. Created vault schema system, operational config, seed decision, and session log.

### [[Dashboard.md]]

- **Score:** 0.690 (recency=0.97, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~456

```dataview TABLE status, created, assigned_session AS "Session" FROM "tasks" WHERE type = "task" AND (status = "open" OR status = "in_progress") SORT created DESC ```

### [[_templates/task.md]]

- **Score:** 0.689 (recency=0.96, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~113

<% tp.file.cursor(2) %>

### [[_templates/knowledge.md]]

- **Score:** 0.688 (recency=0.96, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~111

<% tp.file.cursor(3) %>

### [[_templates/session.md]]

- **Score:** 0.688 (recency=0.96, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~95

<% tp.file.cursor(1) %>

### [[_templates/decision.md]]

- **Score:** 0.687 (recency=0.96, delta=1.00, links=0.00, importance=0.50)
- **Tokens:** ~133

<% tp.file.cursor(5) %>

### [[decisions/DEC-0001.md]]

- **Score:** 0.599 (recency=0.00, delta=1.00, links=1.00, importance=0.50)
- **Tokens:** ~180

Use exactly one level of semantic folders: `_system/`, `decisions/`, `sessions/`, `knowledge/`, `tasks/`.

## Open Tasks

No open tasks.

## Recent Decisions

- **[[decisions/DEC-0001.md|Vault structure — flat folders over nested hierarchy]]** (2026-04-02): Shallow folders (one level) with rich frontmatter. Deep nesting makes path construction fragile — I'd need to know the full tree to create or find a note. Flat-with-tags loses the ability to scope Dataview queries by folder. One level of semantic folders gives both: folder-scoped queries AND simple paths.

## Drift Warnings

Issues detected in `_system/_drift_report.md`:

- **Critical:** 2
- **High:** 3
- **Medium:** 2
- **Low:** 2
