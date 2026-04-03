---
type: dashboard
---

# Vault Dashboard

## Open Tasks

```dataview
TABLE status, created, assigned_session AS "Session"
FROM "tasks"
WHERE type = "task" AND (status = "open" OR status = "in_progress")
SORT created DESC
```

## Recent Decisions

```dataview
TABLE status, date, rationale
FROM "decisions"
WHERE type = "decision"
SORT date DESC
LIMIT 10
```

## Decision Chains

```dataview
TABLE supersedes AS "Supersedes", status
FROM "decisions"
WHERE supersedes != null
SORT date DESC
```

## Active Sessions

```dataview
TABLE agent, status, summary
FROM "sessions"
WHERE type = "session"
SORT date DESC
LIMIT 5
```

## Knowledge Base

```dataview
TABLE subject, confidence, last_verified AS "Verified"
FROM "knowledge"
WHERE type = "knowledge"
SORT last_verified DESC
```

## Stale Knowledge

```dataview
TABLE subject, last_verified AS "Verified", confidence
FROM "knowledge"
WHERE type = "knowledge" AND confidence = "stale"
SORT last_verified ASC
```

## Vault Stats

```dataviewjs
const decisions = dv.pages('"decisions"').where(p => p.type === "decision");
const tasks = dv.pages('"tasks"').where(p => p.type === "task");
const knowledge = dv.pages('"knowledge"').where(p => p.type === "knowledge");
const sessions = dv.pages('"sessions"').where(p => p.type === "session");

dv.table(["Metric", "Count"], [
  ["Decisions (accepted)", decisions.where(d => d.status === "accepted").length],
  ["Decisions (superseded)", decisions.where(d => d.status === "superseded").length],
  ["Tasks (open)", tasks.where(t => t.status === "open" || t.status === "in_progress").length],
  ["Tasks (done)", tasks.where(t => t.status === "done").length],
  ["Knowledge entries", knowledge.length],
  ["Knowledge (stale)", knowledge.where(k => k.confidence === "stale").length],
  ["Sessions (total)", sessions.length],
]);
```
