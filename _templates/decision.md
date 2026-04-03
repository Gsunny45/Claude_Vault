---
type: decision
id: <% "DEC-" + String(Math.max(0, ...app.vault.getMarkdownFiles().filter(f => f.path.startsWith("decisions/DEC-")).map(f => parseInt(f.basename.replace("DEC-","")) || 0)) + 1).padStart(4, "0") %>
title: "<% tp.file.cursor(1) %>"
date: <% tp.date.now("YYYY-MM-DD") %>
status: accepted
context: "<% tp.file.cursor(2) %>"
alternatives:
  - "<% tp.file.cursor(3) %>"
rationale: "<% tp.file.cursor(4) %>"
affects: []
tokens:
---

## Decision

<% tp.file.cursor(5) %>

## Alternatives Considered

1.

## Rationale

