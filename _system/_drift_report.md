---
type: drift_report
scanned: 2026-06-05T02:41:33.401Z
total_notes: 107
issues_found: 97
critical: 0
high: 7
medium: 34
low: 56
---

# Drift Report — 2026-06-05 02:41

## Summary
Scanned 107 notes. Found 97 issues.

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 7 |
| Medium | 34 |
| Low | 56 |

## High Issues

### Stale References
- `knowledge/KNW-0008.md` → `tasks/TSK-0003.md`: target modified 53 days after source was last verified
  - Source verified: 2026-04-06, Target modified: 2026-05-29
- `decisions/DEC-0003.md` → `decisions/DEC-0004.md`: target modified 39 days after source was last verified
  - Source verified: 2026-04-20, Target modified: 2026-05-29

### Schema Violations (Missing Fields)
- `sessions/daily/2026-04-03.md`: missing required field `type` (expected: session)
- `sessions/daily/2026-04-03.md`: missing required field `id` (expected: string)
- `sessions/daily/2026-04-03.md`: missing required field `date` (expected: date)
- `sessions/daily/2026-04-03.md`: missing required field `agent` (expected: enum)
- `sessions/daily/2026-04-03.md`: missing required field `status` (expected: enum)

## Medium Issues

### Stale References
- `sessions/SES-2026-05-27-001.md` → `exports/_archived_2026-05-30/device-setup-note20-moto.md`: target modified 0 days after source was last verified
  - Source verified: 2026-05-27, Target modified: 2026-05-27
- `sessions/SES-2026-05-27-001.md` → `memory/context/api-budgets.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-27, Target modified: 2026-05-27
- `sessions/SES-2026-05-28-001.md` → `exports/inbox/nous_bug_report.md`: target modified 0 days after source was last verified
  - Source verified: 2026-05-28, Target modified: 2026-05-28
- `knowledge/KNW-0022.md` → `decisions/DEC-0006.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-29, Target modified: 2026-05-30
- `knowledge/KNW-0026-vault-alignment-path-plan.md` → `decisions/DEC-0006.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-29, Target modified: 2026-05-30
- `knowledge/KNW-0025-keyboard-vault-injection-tests.md` → `decisions/DEC-0004.md`: target modified 0 days after source was last verified
  - Source verified: 2026-05-29, Target modified: 2026-05-29
- `knowledge/KNW-0025-keyboard-vault-injection-tests.md` → `knowledge/KNW-0024.md`: target modified 0 days after source was last verified
  - Source verified: 2026-05-29, Target modified: 2026-05-29
- `knowledge/KNW-0025-keyboard-vault-injection-tests.md` → `decisions/DEC-0005.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-29, Target modified: 2026-05-30
- `knowledge/KNW-0024.md` → `decisions/DEC-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-28, Target modified: 2026-05-29
- `knowledge/KNW-0024.md` → `decisions/DEC-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-28, Target modified: 2026-05-29
- `knowledge/KNW-0024.md` → `tasks/TSK-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-28, Target modified: 2026-05-29
- `knowledge/KNW-0024.md` → `tasks/TSK-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-28, Target modified: 2026-05-29
- `knowledge/KNW-0002.md` → `knowledge/KNW-0005.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0002.md` → `knowledge/KNW-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0002.md` → `knowledge/KNW-0004.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0002.md` → `knowledge/KNW-0005.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0008.md` → `knowledge/KNW-0009.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-06, Target modified: 2026-04-07
- `knowledge/KNW-0005.md` → `knowledge/KNW-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0004.md` → `knowledge/KNW-0005.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `decisions/DEC-0005.md` → `decisions/DEC-0004.md`: target modified 0 days after source was last verified
  - Source verified: 2026-05-29, Target modified: 2026-05-29
- `decisions/DEC-0004.md` → `decisions/DEC-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-28, Target modified: 2026-05-29
- `decisions/DEC-0004.md` → `tasks/TSK-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-28, Target modified: 2026-05-29
- `decisions/DEC-0004.md` → `knowledge/KNW-0024.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-28, Target modified: 2026-05-29
- `decisions/DEC-0004.md` → `tasks/TSK-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-05-28, Target modified: 2026-05-29

### Schema Violations (Wrong Types)
- `_system/_briefing.md`: field `compiled` is string, expected datetime
- `sessions/SES-2026-04-21-copilot-cli-backend-hang.md`: field `agent` is claude-haiku-4-5, expected enum(claude-code|claude-desktop|claude-api|local)
- `sessions/SES-2026-04-21-copilot-cli-backend-hang.md`: field `status` is archived, expected enum(active|closed)
- `sessions/SES-2026-05-27-001.md`: field `agent` is claude-sonnet-4-6, expected enum(claude-code|claude-desktop|claude-api|local)
- `sessions/SES-2026-05-29-001.md`: field `status` is complete, expected enum(active|closed)
- `sessions/SES-2026-05-28-001.md`: field `agent` is claude-sonnet-4-6 (Cowork), expected enum(claude-code|claude-desktop|claude-api|local)
- `sessions/HANDOFF-claude-design-landing-2026-05-30.md`: field `agent` is claude, expected enum(claude-code|claude-desktop|claude-api|local)
- `sessions/HANDOFF-claude-design-landing-2026-05-30.md`: field `status` is handoff, expected enum(active|closed)
- `sessions/NEXT-SESSION-cte-audit-handoff.md`: field `agent` is claude, expected enum(claude-code|claude-desktop|claude-api|local)
- `sessions/NEXT-SESSION-cte-audit-handoff.md`: field `status` is handoff, expected enum(active|closed)

## Low Issues

### Orphan Notes
- `_templates/weekly.md` — no inbound links, last modified 2026-04-03
- `_templates/task.md` — no inbound links, last modified 2026-04-03
- `_templates/rag-question.md` — no inbound links, last modified 2026-04-09
- `_templates/decision.md` — no inbound links, last modified 2026-04-03
- `_templates/startup.md` — no inbound links, last modified 2026-04-03
- `_templates/session.md` — no inbound links, last modified 2026-04-03
- `_templates/Preloaded Classes/202403091325 General Tweaks CSS Classes.md` — no inbound links, last modified 2026-04-03
- `_templates/Preloaded Classes/202401211512 Notebook CSS Classes.md` — no inbound links, last modified 2026-04-03
- `_templates/knowledge.md` — no inbound links, last modified 2026-04-03
- `_templates/daily.md` — no inbound links, last modified 2026-04-03
- `_scripts/openrouter_mcp/README.md` — no inbound links, last modified 2026-04-10
- `Task_Board.md` — no inbound links, last modified 2026-04-06
- `tasks/TSK-0007.md` — no inbound links, last modified 2026-04-20
- `sessions/SES-2026-05-04-001.md` — no inbound links, last modified 2026-05-04
- `sessions/SES-2026-04-21-copilot-cli-backend-hang.md` — no inbound links, last modified 2026-04-21
- `sessions/SES-2026-04-19-001.md` — no inbound links, last modified 2026-04-20
- `sessions/SES-2026-04-02-001.md` — no inbound links, last modified 2026-04-03
- `sessions/SES-2026-04-06-001.md` — no inbound links, last modified 2026-04-06
- `sessions/SES-2026-04-17-001.md` — no inbound links, last modified 2026-04-20
- `sessions/daily/2026-04-03.md` — no inbound links, last modified 2026-04-20
- `README.md` — no inbound links, last modified 2026-04-03
- `memory/glossary.md` — no inbound links, last modified 2026-05-04
- `memory/projects/llm-orchestrator.md` — no inbound links, last modified 2026-04-13
- `memory/context/api-registry.md` — no inbound links, last modified 2026-04-14
- `knowledge/KNW-0017.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0016.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0020.md` — no inbound links, last modified 2026-04-11
- `knowledge/KNW-0021.md` — no inbound links, last modified 2026-04-14
- `knowledge/KNW-0013.md` — no inbound links, last modified 2026-04-09
- `knowledge/KNW-0019.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0018.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0015.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0014.md` — no inbound links, last modified 2026-04-10
- `knowledge/KNW-0012.md` — no inbound links, last modified 2026-04-09
- `knowledge/KNW-0011.md` — no inbound links, last modified 2026-04-17
- `knowledge/KNW-0006.md` — no inbound links, last modified 2026-04-04
- `knowledge/KNW-0010.md` — no inbound links, last modified 2026-04-11
- `knowledge/KNW-0002.md` — no inbound links, last modified 2026-04-03
- `knowledge/KNW-0007.md` — no inbound links, last modified 2026-04-04
- `knowledge/KNW-0001.md` — no inbound links, last modified 2026-04-03
- `exports/_archived_2026-05-30/MAD_MAX_STATUS.md` — no inbound links, last modified 2026-04-17
- `exports/inbox/Untitled.md` — no inbound links, last modified 2026-04-09
- `exports/inbox/docs-audit-2026-05-03.md` — no inbound links, last modified 2026-05-03
- `exports/inbox/2026-04-26.md` — no inbound links, last modified 2026-04-27
- `exports/inbox/2026-04-15.md` — no inbound links, last modified 2026-04-16
- `exports/inbox/2026-04-14.md` — no inbound links, last modified 2026-04-14
- `exports/inbox/2026-05-17.md` — no inbound links, last modified 2026-05-17
- `exports/inbox/2026-04-06.md` — no inbound links, last modified 2026-04-06
- `exports/inbox/2026-04-20.md` — no inbound links, last modified 2026-04-20
- `exports/inbox/2026-04-11.md` — no inbound links, last modified 2026-04-11
- `exports/inbox/2026-04-08.md` — no inbound links, last modified 2026-04-09
- `exports/inbox/2026-04-05.md` — no inbound links, last modified 2026-04-06
- `exports/inbox/2026-04-04.md` — no inbound links, last modified 2026-04-04
- `decisions/DEC-0002.md` — no inbound links, last modified 2026-04-06
- `decisions/DEC-0001.md` — no inbound links, last modified 2026-04-03
- `Dashboard.md` — no inbound links, last modified 2026-04-03
