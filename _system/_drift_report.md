---
type: drift_report
scanned: 2026-04-14T08:29:31.297Z
total_notes: 158
issues_found: 14
critical: 0
high: 5
medium: 9
low: 0
---

# Drift Report — 2026-04-14 08:29

## Summary
Scanned 158 notes. Found 14 issues.

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 5 |
| Medium | 9 |
| Low | 0 |

## High Issues

### Schema Violations (Missing Fields)
- `sessions/daily/2024-01-26.md`: missing required field `type` (expected: session)
- `sessions/daily/2024-01-26.md`: missing required field `id` (expected: string)
- `sessions/daily/2024-01-26.md`: missing required field `date` (expected: date)
- `sessions/daily/2024-01-26.md`: missing required field `agent` (expected: enum)
- `sessions/daily/2024-01-26.md`: missing required field `status` (expected: enum)

## Medium Issues

### Stale References
- `knowledge/KNW-0008.md` → `tasks/TSK-0003.md`: target modified 0 days after source was last verified
  - Source verified: 2026-04-06, Target modified: 2026-04-06
- `knowledge/KNW-0008.md` → `knowledge/KNW-0009.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-06, Target modified: 2026-04-07
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
- `knowledge/KNW-0004.md` → `knowledge/KNW-0005.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03

### Schema Violations (Wrong Types)
- `_system/_briefing.md`: field `compiled` is string, expected datetime
