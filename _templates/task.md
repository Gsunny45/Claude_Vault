---
type: task
id: <% "TSK-" + String(Math.max(0, ...app.vault.getMarkdownFiles().filter(f => f.path.startsWith("tasks/TSK-")).map(f => parseInt(f.basename.replace("TSK-","")) || 0)) + 1).padStart(4, "0") %>
title: "<% tp.file.cursor(1) %>"
status: open
created: <% tp.date.now("YYYY-MM-DD") %>
assigned_session:
depends_on: []
outcome: ""
---

## Objective

<% tp.file.cursor(2) %>

## Acceptance Criteria

- [ ] <% tp.file.cursor(3) %>

## Progress

