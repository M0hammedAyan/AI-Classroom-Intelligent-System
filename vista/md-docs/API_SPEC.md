# VISTA — API Specification

> **Last Updated:** 2026-06-24
> **Status:** Complete — implemented in `backend/app/routes/`
> **Canonical source:** `docs/API_CONTRACT.md` (frozen Day 3)

---

## 1. API Architecture

- **Framework:** FastAPI
- **Base URL:** `http://127.0.0.1:8002` (configurable via `PORT` / `UVICORN_PORT`)
- **Prefix:** `/api/v1/`
- **Auth:** `Authorization: Bearer <jwt>` on protected endpoints
- **Content-Type:** `application/json` (except export / report endpoints which return CSV / PDF)
- **Error format:** `{"error": {"code": "...", "message": "...", "details": {}}}` or FastAPI standard `{"detail": "..."}`

---

## 2. Endpoint Summary

The production backend implements **114 endpoints** in total (110 route endpoints across 14 modules + 4 root/monitoring/WebSocket endpoints):

| Module | Route Prefix | Endpoints | Key Capabilities |
|---|---|---|---|
| `auth` | `/api/v1/auth` | 7 | Login, logout, me, refresh, password reset, role check |
| `academics` | `/api/v1/academics` | 23 | Classes, subjects, timetables, curriculum management |
| `admin` | `/api/v1/admin` | 29 | User CRUD, org hierarchy, audit logs, system config |
| `attendance` | `/api/v1/attendance` | 8 | Face mark, manual mark, session logs, overrides, stats |
| `dashboards` | `/api/v1/dashboards` | 7 | Scoped KPI analytics for Admin, HOS, HOP, Mentor, Teacher, Student |
| `enroll` | `/api/v1/enroll` / `/students/{id}/enroll` | 2 | Single & batch facial embedding enrollment (SCRFD + ArcFace) |
| `export` | `/api/v1/export` | 1 | Attendance & risk reporting export (CSV) |
| `lms` | `/api/v1/lms` | 4 | Assignments, submissions, syllabus tracking |
| `mentor` | `/api/v1/mentor` | 6 | Student watchlists, intervention logging, mentor notes |
| `notifications` | `/api/v1/notifications` | 4 | In-app alerts, unread counts, mark-as-read |
| `reports` | `/api/v1/reports` | 1 | Academic and attendance PDF/CSV reports |
| `risk` | `/api/v1/risk` | 5 | Flag retrieval, recompute, student risk detail, SHAP explain |
| `student_portal` | `/api/v1/student` | 10 | Attendance history, marks, timetable, assignments, profile |
| `students` | `/api/v1/students` | 3 | Student listing, student profile, registration |
| **System** | `/`, `/health`, `/metrics*`, `/ws` | 4 | Health check, Prometheus metrics, WebSocket dashboard push |

*Baseline Pilot Sub-contract (Day 3 Frozen Core):*
1. `POST /api/v1/auth/login` — Login
2. `POST /api/v1/auth/logout` — Logout
3. `GET /api/v1/students` — List students
4. `GET /api/v1/students/{id}` — Student profile
5. `POST /api/v1/attendance/mark` — Photo attendance marking (via `facial_pipeline.py` or fallback)
6. `GET /api/v1/attendance/log` — Attendance log
7. `PATCH /api/v1/attendance/{id}` — Attendance status override
8. `GET /api/v1/students/{id}/risk` — Single student risk details
9. `GET /api/v1/risk` — Roster risk flags
10. `POST /api/v1/students/{id}/risk/recompute` — Recompute student risk
11. `GET /api/v1/export/report` — Export attendance report (CSV)
12. `POST /api/v1/students/{id}/enroll` — Enroll face embeddings (implemented in `enroll.py`)
13. `GET /health` — Service health check

---

## 3. Authentication Strategy

- JWT created on login with HS256 algorithm
- Payload: `{sub: user_id, role: "admin"|"hos"|"hop"|"mentor"|"teacher"|"student", iat, exp}`
- Expiry: 8 hours default (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Revocation: Redis or in-memory blocklist
- Secret: `VISTA_JWT_SECRET` / `JWT_SECRET_KEY` env var

---

## 4. Authorization Strategy

Role-based access control (RBAC) enforced via FastAPI dependencies in `permissions.py`:
- `get_current_user`: Validates token, loads user record
- `require_role([...])`: Scopes routes to allowed roles: `admin`, `hos`, `hop`, `mentor`, `teacher`, `student`
- `require_admin`: Convenience guard for admin-only management routes

---

## 5. Error Handling Strategy

| HTTP Code | When | Error Code Examples |
|---|---|---|
| 400 | Invalid input | INVALID_IMAGE, INVALID_STATUS, INVALID_DATE_RANGE |
| 401 | Missing/invalid token | MISSING_TOKEN, INVALID_TOKEN, INVALID_CREDENTIALS |
| 403 | Wrong role or disabled account | FORBIDDEN, ACCOUNT_DISABLED |
| 404 | Resource not found | STUDENT_NOT_FOUND, ATTENDANCE_NOT_FOUND |
| 500 | Server error | RISK_COMPUTE_ERROR |

---

## 6. Service Structure

The 14 route modules in `vista/backend/app/routes/` are:
```
routes/academics.py      → Classes, subjects, timetables, and academic structures
routes/admin.py          → User CRUD, organization tree, system configuration, audit logs
routes/attendance.py     → Photo attendance processing, session logging, manual overrides
routes/auth.py           → User authentication, token issuance, and password management
routes/dashboards.py     → Role-scoped metrics and aggregated KPI analytics
routes/enroll.py         → Facial image feature extraction and student enrollment
routes/export.py         → Data export to CSV
routes/lms.py            → Study materials, assignments, and submissions
routes/mentor.py         → Mentorship assignment, student watchlist, intervention tracking
routes/notifications.py  → In-app notifications and broadcast alerts
routes/reports.py        → Detailed academic performance and attendance reporting
routes/risk.py           → Rule-based and ML risk assessment, factor explanations
routes/student_portal.py → Student self-service access to attendance, marks, and timetable
routes/students.py       → Student directory, profiles, and basic CRUD
```

Each route file defines an `APIRouter` with dependencies `Depends(get_db)` and `Depends(get_current_user)`.

---

## 7. Key Design Decisions

1. **Absent entries are derived at read time** — `GET /attendance/log` diffs roster vs present records.
2. **Liveness validation** — Heuristic texture and geometry checks filter static photo spoofs during marking.
3. **Unrecognized faces write NO DB row** — False rejects are logged and evaluated in test suites.
4. **Automated & On-Demand Risk Assessment** — Risk flags are computed on-demand (`POST /risk/recompute`) and automatically daily via APScheduler (`scheduler.py`).
5. **WebSocket Push** — Live metrics and dashboard updates are pushed to connected clients via `/ws/dashboard`.
