---
type: knowledge
id: <% "KNW-" + String(Math.max(0, ...app.vault.getMarkdownFiles().filter(f => f.path.startsWith("knowledge/KNW-")).map(f => parseInt(f.basename.replace("KNW-","")) || 0)) + 1).padStart(4, "0") %>
subject: "<% tp.file.cursor(1) %>"
confidence: verified
last_verified: <% tp.date.now("YYYY-MM-DD") %>
source: "<% tp.file.cursor(2) %>"
related: []
tokens:
---

## Summary

<% tp.file.cursor(3) %>

## Details

## References

