---
type: dashboard
importance: high
---

# Vault Health Dashboard

> Comprehensive operational health metrics for the Claude Vault.
> All sections are live — powered by Dataview and DataviewJS.

---

## 1. Schema Compliance

```dataviewjs
const folders = {
  "decisions": ["type", "id", "status"],
  "sessions":  ["type", "id", "status"],
  "knowledge": ["type", "id", "confidence"],
  "tasks":     ["type", "id", "status"]
};

let rows = [];

for (let [folder, requiredFields] of Object.entries(folders)) {
  let pages = dv.pages(`"${folder}"`);
  let total = pages.length;
  let compliant = 0;
  let nonCompliant = 0;

  for (let p of pages) {
    let hasAll = requiredFields.every(f => p[f] != null && p[f] !== "");
    if (hasAll) {
      compliant++;
    } else {
      nonCompliant++;
    }
  }

  let pct = total > 0 ? Math.round((compliant / total) * 100) : 0;
  let bar = total > 0
    ? (pct === 100 ? "✅ " + pct + "%" : (pct >= 75 ? "⚠️ " + pct + "%" : "❌ " + pct + "%"))
    : "—";

  rows.push([folder, total, compliant, nonCompliant, bar]);
}

dv.table(
  ["Folder", "Total Notes", "Compliant", "Non-Compliant", "Compliance %"],
  rows
);
```

---

## 2. Knowledge Freshness

```dataview
TABLE
  subject AS "Subject",
  confidence AS "Confidence",
  last_verified AS "Last Verified",
  round((date(now) - last_verified).days) AS "Days Since Verified",
  choice(round((date(now) - last_verified).days) > 14, "🔴 STALE", "🟢 Fresh") AS "Status"
FROM "knowledge"
WHERE last_verified
SORT (date(now) - last_verified).days DESC
```

---

## 3. Decision Velocity

```dataviewjs
let decisions = dv.pages('"decisions"').where(d => d.date);

// Group by year-month
let grouped = {};
for (let d of decisions) {
  let dt = dv.date(d.date);
  if (!dt) continue;
  let key = dt.year + "-" + String(dt.month).padStart(2, "0");
  if (!grouped[key]) {
    grouped[key] = { total: 0, accepted: 0, superseded: 0, other: 0 };
  }
  grouped[key].total++;
  let s = (d.status || "").toLowerCase();
  if (s === "accepted" || s === "active") {
    grouped[key].accepted++;
  } else if (s === "superseded" || s === "replaced") {
    grouped[key].superseded++;
  } else {
    grouped[key].other++;
  }
}

let sortedKeys = Object.keys(grouped).sort().reverse();

let rows = sortedKeys.map(k => {
  let g = grouped[k];
  let ratio = g.superseded > 0
    ? (g.accepted / g.superseded).toFixed(1) + ":1"
    : g.accepted + ":0";
  return [k, g.total, g.accepted, g.superseded, g.other, ratio];
});

dv.header(4, "Decisions by Month");
dv.table(
  ["Month", "Total", "Accepted", "Superseded", "Other", "Accepted:Superseded"],
  rows
);

if (sortedKeys.length === 0) {
  dv.paragraph("*No decisions with a `date` field found.*");
}
```

---

## 4. Task Pipeline

```dataviewjs
let tasks = dv.pages('"tasks"');

// Count by status
let statusCounts = {};
let statuses = ["open", "in_progress", "blocked", "done", "cancelled"];
for (let s of statuses) {
  statusCounts[s] = 0;
}

for (let t of tasks) {
  let s = (t.status || "unknown").toLowerCase();
  if (statusCounts[s] !== undefined) {
    statusCounts[s]++;
  } else {
    if (!statusCounts["other"]) statusCounts["other"] = 0;
    statusCounts["other"]++;
  }
}

let statusRows = Object.entries(statusCounts)
  .filter(([_, count]) => count > 0)
  .map(([status, count]) => {
    let icon = {
      "open": "🟡", "in_progress": "🔵", "blocked": "🔴",
      "done": "✅", "cancelled": "⚫", "other": "❓"
    }[status] || "❓";
    return [icon + " " + status, count];
  });

dv.header(4, "Status Breakdown");
dv.table(["Status", "Count"], statusRows);

// Average age of open tasks
let openTasks = tasks.where(t => {
  let s = (t.status || "").toLowerCase();
  return s === "open" || s === "in_progress" || s === "blocked";
});

if (openTasks.length > 0) {
  let now = dv.date("now");
  let ages = [];
  let oldest = null;
  let oldestAge = -1;

  for (let t of openTasks) {
    let created = t.created || t.date || t.file.cday;
    if (created) {
      let dt = dv.date(created);
      if (dt) {
        let ageDays = Math.round((now - dt).days);
        ages.push(ageDays);
        if (ageDays > oldestAge) {
          oldestAge = ageDays;
          oldest = t;
        }
      }
    }
  }

  if (ages.length > 0) {
    let avgAge = Math.round(ages.reduce((a, b) => a + b, 0) / ages.length);
    dv.header(4, "Open Task Metrics");
    dv.paragraph("**Active tasks:** " + openTasks.length);
    dv.paragraph("**Average age:** " + avgAge + " days");
    dv.paragraph("**Oldest open task:** " + oldest.file.link + " (" + oldestAge + " days)");
  }
} else {
  dv.paragraph("*No open tasks found.*");
}
```

---

## 5. Session Activity

```dataview
TABLE
  date AS "Date",
  agent AS "Agent",
  status AS "Status",
  length(files_written) AS "Files Written"
FROM "sessions"
SORT date DESC
LIMIT 10
```

---

## 6. Link Density

```dataviewjs
// Exclude system and template folders from content analysis
let contentPages = dv.pages("")
  .where(p => !p.file.path.startsWith("_system/") && !p.file.path.startsWith("_templates/"));

let allPages = dv.pages("");

// Count outbound links per note
let totalLinks = 0;
let inboundCounts = {};

// Initialize inbound counts for all pages
for (let p of allPages) {
  inboundCounts[p.file.path] = 0;
}

// Count outbound links and track inbound
for (let p of contentPages) {
  let outLinks = p.file.outlinks || [];
  totalLinks += outLinks.length;

  for (let link of outLinks) {
    let target = link.path;
    if (target && inboundCounts[target] !== undefined) {
      inboundCounts[target]++;
    }
  }
}

let noteCount = contentPages.length;
let avgLinks = noteCount > 0 ? (totalLinks / noteCount).toFixed(1) : 0;

dv.header(4, "Overall Link Statistics");
dv.paragraph("**Total internal links:** " + totalLinks);
dv.paragraph("**Content notes:** " + noteCount);
dv.paragraph("**Average links per note:** " + avgLinks);

// Most linked-to note
let maxInbound = 0;
let mostLinked = null;
for (let [path, count] of Object.entries(inboundCounts)) {
  if (count > maxInbound) {
    maxInbound = count;
    mostLinked = path;
  }
}

if (mostLinked) {
  dv.header(4, "Most-Linked-To Note");
  dv.paragraph("**" + dv.fileLink(mostLinked) + "** with " + maxInbound + " inbound links");
}

// Orphan notes (zero inbound links, not in _system or _templates)
let orphans = [];
for (let p of contentPages) {
  let inbound = inboundCounts[p.file.path] || 0;
  if (inbound === 0) {
    orphans.push(p.file.link);
  }
}

dv.header(4, "Orphan Notes (0 inbound links)");
if (orphans.length > 0) {
  dv.paragraph("Found **" + orphans.length + "** orphan note(s):");
  dv.list(orphans);
} else {
  dv.paragraph("*No orphan notes found — all content notes have at least one inbound link.*");
}
```

---

## 7. Token Budget

```dataviewjs
const BRIEFING_BUDGET = 8000;

let allPages = dv.pages("").where(p => p.tokens != null);

let totalTokens = 0;
let byFolder = {};

for (let p of allPages) {
  let tokens = Number(p.tokens) || 0;
  totalTokens += tokens;

  let folder = p.file.folder || "(root)";
  // Normalize to top-level folder
  let topFolder = folder.split("/")[0] || "(root)";
  if (!byFolder[topFolder]) byFolder[topFolder] = 0;
  byFolder[topFolder] += tokens;
}

let pctOfBriefing = totalTokens > 0
  ? ((BRIEFING_BUDGET / totalTokens) * 100).toFixed(1)
  : "N/A";

dv.header(4, "Token Summary");
dv.paragraph("**Total estimated tokens in vault:** " + totalTokens.toLocaleString());
dv.paragraph("**Briefing budget:** " + BRIEFING_BUDGET.toLocaleString() + " tokens");
dv.paragraph("**Vault coverage in one briefing:** " + pctOfBriefing + "%");

let folderRows = Object.entries(byFolder)
  .sort((a, b) => b[1] - a[1])
  .map(([folder, tokens]) => {
    let pct = totalTokens > 0 ? Math.round((tokens / totalTokens) * 100) : 0;
    return [folder, tokens.toLocaleString(), pct + "%"];
  });

if (folderRows.length > 0) {
  dv.header(4, "Breakdown by Folder");
  dv.table(["Folder", "Tokens", "% of Total"], folderRows);
} else {
  dv.paragraph("*No notes with a `tokens` field found. Add `tokens:` to note frontmatter to enable budget tracking.*");
}
```

---

## 8. Drift Summary

> Full report: [[_system/_drift_report]]

```dataviewjs
let report = dv.page("_system/_drift_report");

if (report) {
  let issuesFound = report.issues_found;
  let critical = report.critical ?? 0;
  let high = report.high ?? 0;
  let medium = report.medium ?? 0;
  let low = report.low ?? 0;

  if (issuesFound != null) {
    dv.header(4, "Drift Report Summary");
    dv.paragraph("**Total issues found:** " + issuesFound);

    let rows = [
      ["🔴 Critical", critical],
      ["🟠 High", high],
      ["🟡 Medium", medium],
      ["🔵 Low", low]
    ];
    dv.table(["Severity", "Count"], rows);

    if (critical > 0) {
      dv.paragraph("> **⚠ CRITICAL DRIFT DETECTED** — Immediate attention required.");
    } else if (high > 0) {
      dv.paragraph("> **⚠ High-severity drift present** — Review recommended.");
    } else if (issuesFound === 0) {
      dv.paragraph("> ✅ **No drift detected.** Vault is in good shape.");
    }
  } else {
    dv.paragraph("*Drift report exists but has no `issues_found` field in frontmatter.*");
  }
} else {
  dv.paragraph("*No drift report found at `_system/_drift_report.md`. Run a drift check to generate one.*");
}
```

---

*Dashboard generated for AI-operated vault monitoring. All queries are live and update automatically when Obsidian reloads or Dataview refreshes.*
