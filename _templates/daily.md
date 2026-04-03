---
type: daily
date: <% tp.date.now("YYYY-MM-DD") %>
---

# Daily Log — <% tp.date.now("YYYY-MM-DD") %>

## Sessions Today

```dataview
TABLE agent, status, summary
FROM "sessions"
WHERE type = "session" AND date = date("<% tp.date.now("YYYY-MM-DD") %>")
SORT file.ctime ASC
```

## Decisions Made Today

```dataview
TABLE title, status, rationale
FROM "decisions"
WHERE type = "decision" AND date = date("<% tp.date.now("YYYY-MM-DD") %>")
```

## Tasks Touched Today

```dataview
TABLE title, status
FROM "tasks"
WHERE type = "task" AND (created = date("<% tp.date.now("YYYY-MM-DD") %>") OR completed = date("<% tp.date.now("YYYY-MM-DD") %>"))
```

## Inbox Captures

![[inbox/<% tp.date.now("YYYY-MM-DD") %>]]

## Notes

