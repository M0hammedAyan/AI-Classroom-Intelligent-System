# CLAUDE.md — frontend/ (Member 3: Frontend & Dashboard Lead)

## Project Context
VISTA is an AI classroom management platform providing automated facial attendance marking and predictive student risk detection.
**Implementation Scope:** Full 6-role workspace (Admin, HOS, HOP, Mentor, Teacher, Student) built with React 19, Vite, and Tailwind CSS v4.

## Your Module's Job
Build and maintain the UI against `docs/API_CONTRACT.md` and the FastAPI backend running on port 8002 (proxied via `vite.config.js`).

## Pages & Role Dashboards
The application provides scoped dashboards and views across all 6 roles:
- `Login.jsx` — Authentication and role-based redirect
- **Admin:** Institution tree, User CRUD, Role permissions, Analytics, System audit logs
- **HOS:** School KPI summary, Department performance, Staff directory, Student analytics
- **HOP:** Department risk center, Class and timetable assignments, Teacher subject mapping
- **Mentor:** Assigned student watchlist, SHAP factor breakdown, Intervention logging
- **Teacher:** Today's timetable, Photo attendance marking, Attendance log & overrides, Marks entry
- **Student:** Personal attendance breakdown, Timetable, Internal assessment marks, Study materials

## Integration Rule
All backend calls go through `src/api/client.js` with Axios, using the `http://localhost:8002/api/v1` base URL. Live metrics and alerts update via WebSocket (`/ws/dashboard`).

## Contract Reference (build mocks matching this exactly)
| Endpoint | Method | Response shape |
|---|---|---|
| `/api/v1/auth/login` | POST | `{token, role, user_id, name}` |
| `/api/v1/attendance/mark` | POST | `{marked_count, records: [...]}` |
| `/api/v1/attendance/log` | GET | `[{student_id, name, status, timestamp}]` |
| `/api/v1/students/{id}/risk` | GET | `{student_id, risk_level, reasons, recommendations}` |
| `/api/v1/students` | GET | `[{student_id, name, class}]` |
| `/api/v1/export/report` | GET | PDF/CSV file |
| `/ws/dashboard` | WebSocket | Real-time KPI broadcasts |

Check `docs/API_CONTRACT.md` and `md-docs/API_SPEC.md` for full endpoint details.

## Hard Rules
- Maintain consistency with the 114 endpoints and 6 roles implemented in backend.
- Use Tailwind CSS v4 design tokens and responsive classes. Dark/light mode toggle supported.

## File/Naming Conventions
camelCase for JS variables/functions, PascalCase for component filenames (`Login.jsx`,
not `login.jsx`).

---

## Agent Response Convention

After completing any task in this module, always end your response with this block:

**Built:** [1–2 sentences — what was just implemented or changed in `frontend/`]  
**Next:** [1–2 specific actionable next steps for this module]

Keep it short. One short paragraph maximum per section. No long summaries unless the user explicitly asks for one.

<!-- reticle:begin (managed by `reticle init` — edit outside these markers) -->
## Verifying with Reticle

This app is instrumented by **Reticle** — an in-app verification layer exposed as `reticle_*` MCP tools and the `reticle` CLI. Verifying is part of "done", not an optional extra.

- **When:** after you build or change any user-facing feature, flow, or UI, verify it with Reticle **before** telling the user it is complete. Reading the code or passing unit tests is not enough — drive the real running app.
- **How:** drive the actual flow (`reticle_act` / `reticle_act_and_wait`), then read the observable effect (`reticle_assert`, `reticle_snapshot`, `reticle_state`, `reticle_network`). Confirm the change produced the effect it was meant to, with no new console errors or failed requests.
- **Covered flows:** run `reticle gate` — it reports which recorded flows the changed files affect and whether they still pass.
- **Never weaken a check to make it green.** Downgrading, skipping, or deleting an assertion is a finding, not a fix.
- **If Reticle can't run** (no daemon, or this is not a running web app), say so — do not skip verification silently.
<!-- reticle:end -->
