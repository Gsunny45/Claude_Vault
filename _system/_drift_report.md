---
type: drift_report
scanned: 2026-04-04T17:43:07.832Z
total_notes: 32
issues_found: 13
critical: 1
high: 5
medium: 7
low: 0
---

# Drift Report — 2026-04-04 17:43

## Summary
Scanned 32 notes. Found 13 issues.

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High | 5 |
| Medium | 7 |
| Low | 0 |

## Critical Issues

### Duplicate IDs
- `knowledge/KNW-0006.md` and `13 keyboard shortcuts.md` both claim id: `KNW-0006` — **one must be renamed**

## High Issues

### Schema Violations (Missing Fields)
- `sessions/daily/2024-01-26.md`: missing required field `type` (expected: session)
- `sessions/daily/2024-01-26.md`: missing required field `id` (expected: string)
- `sessions/daily/2024-01-26.md`: missing required field `date` (expected: date)
- `sessions/daily/2024-01-26.md`: missing required field `agent` (expected: enum)
- `sessions/daily/2024-01-26.md`: missing required field `status` (expected: enum)

## Medium Issues

### Stale References
- `knowledge/KNW-0005.md` → `knowledge/KNW-0003.md`: target modified 1 days after source was last verified
  - Source verified: 2026-04-02, Target modified: 2026-04-03
- `knowledge/KNW-0004.md` → `knowledge/KNW-0005.md`: target modified 1 days after source was last verified
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
