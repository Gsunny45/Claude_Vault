---
type: drift_report
scanned: 2026-05-17T18:48:07.338Z
total_notes: 79
issues_found: 60
critical: 0
high: 6
medium: 10
low: 44
---

# Drift Report — 2026-05-17 18:48

## Summary
Scanned 79 notes. Found 60 issues.

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 6 |
| Medium | 10 |
| Low | 44 |

## High Issues

### Stale References
- `knowledge/KNW-0008.md` → `tasks/TSK-0003.md`: target modified 15 days after source was last verified
  - Source verified: 2026-04-06, Target modified: 2026-04-20

### Schema Violations (Missing Fields)
- `sessions/daily/2026-04-03.md`: missing required field `type` (expected: session)
- `sessions/daily/2026-04-03.md`: missing required field `id` (expected: string)
- `sessions/daily/2026-04-03.md`: missing required field `date` (expected: date)
- `sessions/daily/2026-04-03.md`: missing required field `agent` (expected: enum)
- `sessions/daily/2026-04-03.md`: missing required field `status` (expected: enum)

## Medium Issues

### Stale References
- `knowledge/KNW-0008.md` → `knowledge/KNW-0009.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-06, Target modified: 2026-04-07
- `knowledge/KNW-0004.md` → `knowledge/KNW-0005.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0005.md` → `knowledge/KNW-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0002.md` → `knowledge/KNW-0005.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0002.md` → `knowledge/KNW-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0002.md` → `knowledge/KNW-0004.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0002.md` → `knowledge/KNW-0005.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03

### Schema Violations (Wrong Types)
- `_system/_briefing.md`: field `compiled` is string, expected datetime
- `sessions/SES-2026-04-21-copilot-cli-backend-hang.md`: field `agent` is claude-haiku-4-5, expected enum(claude-code|claude-desktop|claude-api|local)
- `sessions/SES-2026-04-21-copilot-cli-backend-hang.md`: field `status` is archived, expected enum(active|closed)

## Low Issues

### Orphan Notes
- `_templates/weekly.md` — no inbound links, last modified 2026-04-03
- `_templates/task.md` — no inbound links, last modified 2026-04-03
- `_templates/startup.md` — no inbound links, last modified 2026-04-03
- `_templates/session.md` — no inbound links, last modified 2026-04-03
- `_templates/rag-question.md` — no inbound links, last modified 2026-04-09
- `_templates/Preloaded Classes/202401211512 Notebook CSS Classes.md` — no inbound links, last modified 2026-04-03
- `_templates/Preloaded Classes/202403091325 General Tweaks CSS Classes.md` — no inbound links, last modified 2026-04-03
- `_templates/knowledge.md` — no inbound links, last modified 2026-04-03
- `_templates/decision.md` — no inbound links, last modified 2026-04-03
- `_templates/daily.md` — no inbound links, last modified 2026-04-03
- `Task_Board.md` — no inbound links, last modified 2026-04-06
- `_scripts/openrouter_mcp/README.md` — no inbound links, last modified 2026-04-10
- `sessions/SES-2026-04-06-001.md` — no inbound links, last modified 2026-04-06
- `sessions/SES-2026-04-02-001.md` — no inbound links, last modified 2026-04-03
- `README.md` — no inbound links, last modified 2026-04-03
- `memory/projects/llm-orchestrator.md` — no inbound links, last modified 2026-04-13
- `memory/context/api-registry.md` — no inbound links, last modified 2026-04-14
- `MAD_MAX_STATUS.md` — no inbound links, last modified 2026-04-17
- `knowledge/KNW-0021.md` — no inbound links, last modified 2026-04-14
- `knowledge/KNW-0020.md` — no inbound links, last modified 2026-04-11
- `knowledge/KNW-0019.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0018.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0017.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0016.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0015.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0014.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0013.md` — no inbound links, last modified 2026-04-09
- `knowledge/KNW-0012.md` — no inbound links, last modified 2026-04-09
- `knowledge/KNW-0011.md` — no inbound links, last modified 2026-04-17
- `knowledge/KNW-0010.md` — no inbound links, last modified 2026-04-11
- `knowledge/KNW-0007.md` — no inbound links, last modified 2026-04-04
- `knowledge/KNW-0008.md` — no inbound links, last modified 2026-04-06
- `knowledge/KNW-0006.md` — no inbound links, last modified 2026-04-04
- `knowledge/KNW-0002.md` — no inbound links, last modified 2026-04-03
- `knowledge/KNW-0001.md` — no inbound links, last modified 2026-04-03
- `inbox/Untitled.md` — no inbound links, last modified 2026-04-09
- `inbox/2026-04-14.md` — no inbound links, last modified 2026-04-14
- `inbox/2026-04-11.md` — no inbound links, last modified 2026-04-11
- `inbox/2026-04-08.md` — no inbound links, last modified 2026-04-09
- `inbox/2026-04-06.md` — no inbound links, last modified 2026-04-06
- `inbox/2026-04-05.md` — no inbound links, last modified 2026-04-06
- `inbox/2026-04-04.md` — no inbound links, last modified 2026-04-04
- `Dashboard.md` — no inbound links, last modified 2026-04-03
- `CLAUDE.md` — no inbound links, last modified 2026-04-20
