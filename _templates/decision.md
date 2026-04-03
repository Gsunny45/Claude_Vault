---
type: decision
id: <% tp.user.next_id("DEC", "decisions") %>
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

