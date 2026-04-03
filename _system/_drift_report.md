---
type: drift_report
scanned: 2026-04-03T08:45:33.450Z
total_notes: 22
issues_found: 7
critical: 0
high: 0
medium: 7
low: 0
---

# Drift Report — 2026-04-03 08:45

## Summary
Scanned 22 notes. Found 7 issues.

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 7 |
| Low | 0 |

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
