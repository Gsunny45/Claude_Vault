---
type: reference
importance: high
---

# Query Library

Reusable Dataview queries for vault operations. Copy into any note or run from Dataview console.

## Find All Decisions Affecting a Path

```dataview
TABLE title, status, date, rationale
FROM "decisions"
WHERE type = "decision" AND contains(affects, "TARGET_PATH_HERE")
SORT date DESC
```

## Active Decision Chain for a Topic

```dataview
TABLE title, status, supersedes, date
FROM "decisions"
WHERE type = "decision" AND (status = "accepted" OR status = "superseded")
SORT date ASC
```

## Knowledge Needing Re-verification

```dataview
TABLE subject, last_verified, confidence, source
FROM "knowledge"
WHERE type = "knowledge" AND (confidence = "stale" OR (date(now) - last_verified).days > 14)
SORT last_verified ASC
```

## Blocked Tasks and Their Dependencies

```dataview
TABLE title, depends_on, created
FROM "tasks"
WHERE type = "task" AND status = "blocked"
SORT created ASC
```

## Sessions by Agent Type

```dataviewjs
const sessions = dv.pages('"sessions"').where(s => s.type === "session");
const agents = {};
sessions.forEach(s => {
  const a = s.agent || "unknown";
  agents[a] = (agents[a] || 0) + 1;
});
dv.table(["Agent", "Session Count"], Object.entries(agents).sort((a,b) => b[1] - a[1]));
```

## Most Connected Notes (Highest Inbound Links)

```dataviewjs
const links = {};
dv.pages().forEach(p => {
  (p.file.outlinks || []).forEach(link => {
    const target = link.path;
    links[target] = (links[target] || 0) + 1;
  });
});
const sorted = Object.entries(links).sort((a,b) => b[1] - a[1]).slice(0, 15);
dv.table(["Note", "Inbound Links"], sorted.map(([path, count]) => [dv.fileLink(path), count]));
```

## Recently Modified Notes (Last 7 Days)

```dataview
TABLE file.mtime AS "Modified", type
WHERE file.mtime >= date(now) - dur(7 days)
SORT file.mtime DESC
LIMIT 20
```

## Orphan Notes (No Inbound Links)

```dataviewjs
const allFiles = dv.pages().where(p => !p.file.path.startsWith("_system/") && !p.file.path.startsWith("_templates/"));
const linked = new Set();
dv.pages().forEach(p => {
  (p.file.outlinks || []).forEach(link => linked.add(link.path));
});
const orphans = allFiles.where(p => !linked.has(p.file.path));
dv.table(["Orphan Note", "Type", "Modified"], orphans.map(p => [p.file.link, p.type || "—", p.file.mtime]).array());
```

## Vault Token Budget Overview

```dataviewjs
const pages = dv.pages().where(p => p.tokens);
const byFolder = {};
let total = 0;
pages.forEach(p => {
  const folder = p.file.folder || "(root)";
  byFolder[folder] = (byFolder[folder] || 0) + p.tokens;
  total += p.tokens;
});
dv.paragraph(`**Total estimated tokens:** ${total} / 8000 briefing budget (${Math.round(total/80)}% capacity)`);
dv.table(["Folder", "Tokens"], Object.entries(byFolder).sort((a,b) => b[1] - a[1]));
```
