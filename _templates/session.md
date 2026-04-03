---
type: session
id: <% "SES-" + tp.date.now("YYYY-MM-DD") + "-001" %>
date: <% tp.date.now("YYYY-MM-DD") %>
agent: claude-code
status: active
files_read: []
files_written: []
decisions_made: []
summary: "<% tp.file.cursor(1) %>"
---

# Session — <% tp.date.now("YYYY-MM-DD") %>

## Context

<% tp.file.cursor(2) %>

## What Was Done

<% tp.file.cursor(3) %>

## What's Next

