# CLAUDE.md — frontend/ (Member 3: Frontend & Dashboard Lead)

## Project Context
VISTA is a 4-person college MVP: face-recognition attendance + academic risk flagging.
**Current scope: pilot only — one classroom, 20–30 students, one dashboard.** The
original report's separate Admin/Teacher/Student dashboards are Phase 2 — build a
single role-gated dashboard for now, not three.

## Your Module's Job
Build the UI against `docs/API_CONTRACT.md`, using Backend's `mock_server/` or mocked
JSON matching that contract. **Do not wait for the real backend to exist** — that's the
entire point of the contract being frozen Day 3.

## Pages (pilot scope only)
- `Login.jsx` — role-gated login (admin/teacher)
- `Dashboard.jsx` — overview: attendance summary + risk flags at a glance
- `AttendanceLog.jsx` — per-classroom attendance log, filterable by date
- `RiskFlags.jsx` — list of flagged students with risk level + reasons

## Integration Rule
All backend calls go through `src/api/client.js` — nowhere else. When Backend's real
API goes live (~Week 7), the only change needed is the base URL in that one file. If
you call endpoints directly from components instead, that swap becomes a multi-file
refactor instead of a one-line change.

## Contract Reference (build mocks matching this exactly)
| Endpoint | Method | Response shape |
|---|---|---|
| `/api/auth/login` | POST | `{token, role}` |
| `/api/attendance/mark` | POST | `{student_id, name, confidence, status}` |
| `/api/attendance/log` | GET | `[{student_id, name, status, timestamp}]` |
| `/api/students/{id}/risk` | GET | `{student_id, risk_level, reasons}` |
| `/api/students` | GET | `[{student_id, name, class}]` |
| `/api/export/report` | GET | PDF/CSV file |

Check `docs/API_CONTRACT.md` for the current version — Member 2 owns it and may have
finalized details beyond this draft.

## Hard Rules
- Mock data must match the contract shape exactly, including field names — sloppy
  mocks here are what cause the Week 7 integration to break.
- This is a pilot demo, not an investor-ready product yet. Functional and clean beats
  pixel-perfect. Don't sink hours into polish the timeline doesn't have room for.

## Explicitly Out of Scope Right Now
- Separate Teacher/Mentor/Admin dashboards (Phase 2)
- Real-time alerts / live updates
- Performance graph library beyond basic charts

## File/Naming Conventions
camelCase for JS variables/functions, PascalCase for component filenames (`Login.jsx`,
not `login.jsx`).

---

## Agent Response Convention

After completing any task in this module, always end your response with this block:

**Built:** [1–2 sentences — what was just implemented or changed in `frontend/`]  
**Next:** [1–2 specific actionable next steps for this module]

Keep it short. One short paragraph maximum per section. No long summaries unless the user explicitly asks for one.
