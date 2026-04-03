---
type: weekly
week_start: <% tp.date.now("YYYY-MM-DD", 0, tp.date.now("YYYY-MM-DD"), "YYYY-MM-DD") %>
---

# Weekly Review — <% tp.date.now("YYYY-[W]ww") %>

## Decision Summary

```dataview
TABLE title, status, date
FROM "decisions"
WHERE type = "decision" AND date >= date("<% tp.date.now("YYYY-MM-DD", -7) %>")
SORT date DESC
```

## Task Throughput

```dataviewjs
const tasks = dv.pages('"tasks"').where(t => t.type === "task");
const done = tasks.where(t => t.status === "done").length;
const open = tasks.where(t => t.status === "open" || t.status === "in_progress").length;
const blocked = tasks.where(t => t.status === "blocked").length;

dv.table(["Status", "Count"], [
  ["Done", done],
  ["Open", open],
  ["Blocked", blocked],
]);
```

## Knowledge Added

```dataview
TABLE subject, confidence
FROM "knowledge"
WHERE type = "knowledge" AND last_verified >= date("<% tp.date.now("YYYY-MM-DD", -7) %>")
SORT last_verified DESC
```

## Session Count

```dataviewjs
const sessions = dv.pages('"sessions"').where(s => s.type === "session");
dv.paragraph("**Total sessions this week:** " + sessions.length);
```

## Drift Trends

- Current drift issues: check [[_system/_drift_report]]
- Stale knowledge to re-verify:

```dataview
LIST
FROM "knowledge"
WHERE type = "knowledge" AND confidence = "stale"
```

## Retrospective

### What worked well

### What needs attention

### Priorities for next week

