# VISTA Integration Log

This file is the single source of truth for any change to `API_CONTRACT.md` or
`DB_SCHEMA.md` made **after the Day 3 contract freeze**, and for any blocker or
test result that affects another team member's work.

**Log an entry when you:**
- Change an API endpoint, request/response field, or DB column after Day 3
- Hit a blocker that stops another member's module from progressing
- Get real accuracy or test numbers from vision or ML — log the honest result, not the target
- Hit, miss, or delay an integration checkpoint

**Format:**
```
## [YYYY-MM-DD] — Member [N] — [Type: Contract Change | Blocker | Test Result | Checkpoint]
What happened / changed:
Impact on other members:
Action needed (if any):
```

One entry per change. If one PR touches three endpoints, log three entries. If a number is
bad, log the bad number — a demo that breaks because someone hid a known issue here is worse
than one that breaks for a reason everyone already knew about.

---

## Log

| Date | Author | Change | Affected Modules | Status |
|---|---|---|---|---|
| 2026-06-21 | Member 2 | OQ-1 resolved: liveness failure writes a row with candidate `student_id` (nullable) — does not mark present | vision, backend, frontend | merged |
| 2026-06-21 | Member 2 | OQ-2 resolved: unrecognized faces write no DB row; false-reject rate measured in `test_recognize.py` | vision | merged |
| 2026-06-21 | Member 2 | OQ-3 resolved: risk recompute is manual, admin-only; no scheduled automation in pilot | ml, backend | merged |
| 2026-06-21 | Member 2 | OQ-4 resolved: JWT expiry 8 hrs, no refresh endpoint in pilot | backend, frontend | merged |
| 2026-06-21 | Member 2 | OQ-5 resolved: absent marking derived at read time in GET /attendance/log — no "close session" endpoint | backend, frontend | merged |

---

## Status Values

| Value | Meaning |
|---|---|
| `proposed` | Change is under discussion, not yet merged |
| `merged` | Change is in `main`; other modules must update |
| `reverted` | Change was rolled back; previous behaviour restored |
| `blocked` | Work is stalled pending another member's input |
