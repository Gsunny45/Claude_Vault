---
type: dashboard
importance: critical
---

# Vault Dashboard

> **Quick Actions**  `BUTTON[compile-briefing]`  `BUTTON[drift-scan]`  `BUTTON[new-decision]`  `BUTTON[new-task]`  `BUTTON[quick-capture]`

```meta-bind-button
label: "Compile Briefing"
id: compile-briefing
style: primary
actions:
  - type: command
    command: context-compiler:compile-briefing
```

```meta-bind-button
label: "Drift Scan"
id: drift-scan
style: destructive
actions:
  - type: command
    command: drift-detector:run-drift-scan
```

```meta-bind-button
label: "+ Decision"
id: new-decision
style: default
actions:
  - type: command
    command: decision-ledger:create-new-decision
```

```meta-bind-button
label: "+ Task"
id: new-task
style: default
actions:
  - type: command
    command: quickadd:choice:qa-new-task
```

```meta-bind-button
label: "Capture"
id: quick-capture
style: default
actions:
  - type: command
    command: quickadd:choice:qa-inbox
```

---

## Open Tasks

```dataview
TABLE WITHOUT ID
  file.link AS "Task",
  status AS "Status",
  created AS "Created",
  assigned_session AS "Session"
FROM "tasks"
WHERE type = "task" AND (status = "open" OR status = "in_progress" OR status = "blocked")
SORT choice(status, "in_progress", 1, "blocked", 2, "open", 3) ASC
```

## Recent Decisions

```dataview
TABLE WITHOUT ID
  file.link AS "Decision",
  status AS "Status",
  date AS "Date",
  rationale AS "Rationale"
FROM "decisions"
WHERE type = "decision"
SORT date DESC
LIMIT 10
```

## Decision Chains

```dataview
TABLE WITHOUT ID
  file.link AS "Decision",
  supersedes AS "Supersedes",
  status AS "Status"
FROM "decisions"
WHERE supersedes != null
SORT date DESC
```

## Active Sessions

```dataview
TABLE WITHOUT ID
  file.link AS "Session",
  agent AS "Agent",
  status AS "Status",
  summary AS "Summary"
FROM "sessions"
WHERE type = "session"
SORT date DESC
LIMIT 5
```

## Knowledge Base

```dataview
TABLE WITHOUT ID
  file.link AS "Entry",
  subject AS "Subject",
  confidence AS "Confidence",
  last_verified AS "Verified"
FROM "knowledge"
WHERE type = "knowledge"
SORT last_verified DESC
```

## Stale Knowledge

```dataview
TABLE WITHOUT ID
  file.link AS "Entry",
  subject AS "Subject",
  last_verified AS "Verified"
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
  ["Tasks (blocked)", tasks.where(t => t.status === "blocked").length],
  ["Tasks (done)", tasks.where(t => t.status === "done").length],
  ["Knowledge entries", knowledge.length],
  ["Knowledge (stale)", knowledge.where(k => k.confidence === "stale").length],
  ["Sessions (total)", sessions.length],
]);
```

---

> [[Vault_Health|Deep Health Metrics]] | [[_system/queries|Query Library]] | [[_system/_briefing|Latest Briefing]] | [[_system/_drift_report|Drift Report]]
