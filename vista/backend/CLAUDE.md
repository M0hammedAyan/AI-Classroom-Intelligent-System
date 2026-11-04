# CLAUDE.md — backend/ (Member 2: Backend & Database Lead)

## Project Context
VISTA is a 4-person college MVP: face-recognition attendance + academic risk flagging.
**Current scope: pilot only — one classroom, 20–30 students.** This is NOT the 80–100
student / multi-college / multi-tenant SaaS spec. Do not build for scale you don't have
a customer for yet.

You own the contract the rest of the team builds against. Get it right and published
early — everyone else is blocked on your decisions for Days 1–3, nobody after that.

## Your Module's Job
1. Finalize and publish `docs/API_CONTRACT.md` and `docs/DB_SCHEMA.md` by Day 3.
2. Stand up `mock_server/` immediately after — returns fake-but-correctly-shaped JSON
   matching the contract, so Frontend (Member 3) never waits on you.
3. Build the real FastAPI app, auth, and DB.
4. Wire in Vision (`vision.recognize()`) and Risk (`ml.risk_engine.calculate_risk()`) —
   import their functions, don't reimplement their logic.

## Contract & Endpoints
The backend runs on **port 8002** by default (configurable via `PORT` / `UVICORN_PORT`) under the `/api/v1/` prefix. It implements **114 endpoints** in total (110 route endpoints across 14 modules + 4 system endpoints).

Key route modules in `app/routes/`:
- `academics.py` (23 endpoints): Classes, sections, subjects, timetables
- `admin.py` (29 endpoints): User management, org tree, audit logs
- `attendance.py` (8 endpoints): Photo attendance, manual mark, session logs
- `auth.py` (7 endpoints): Login, logout, current user, tokens
- `dashboards.py` (7 endpoints): Role-scoped analytics for 3 active roles (admin, teacher, student)
- `enroll.py` (2 endpoints): Face registration (single & batch)
- `export.py` (1 endpoint): CSV attendance reports
- `lms.py` (4 endpoints): Course materials, assignments, submissions
- `mentor.py` (6 endpoints): Watchlists, interventions, mentor notes
- `notifications.py` (4 endpoints): Alerts and broadcast messages
- `reports.py` (1 endpoint): PDF/CSV reports
- `risk.py` (5 endpoints): Risk flags, on-demand recomputation, SHAP explain
- `student_portal.py` (10 endpoints): Student self-service access
- `students.py` (3 endpoints): Student profile and listings

Root & System endpoints:
- `GET /health` — Service health check
- `GET /metrics` & `/metrics/json` — Prometheus metrics
- `WebSocket /ws/dashboard` — Live dashboard broadcast

## Structure
- `app/routes/` — 14 route files
- `app/models/` — 8 model files defining 27 tables (organization, user, student, attendance, timetable, notification, intervention, audit)
- `app/db.py`, `app/main.py`
- `app/scheduler.py` — APScheduler automated daily risk recalculation
- `app/websocket.py` — WebSocket connection manager
- `app/monitoring.py` — Prometheus instrumentation
- `app/cache.py` — Redis with in-memory caching
- `mock_server/` — mock server for testing

## Hard Rules
- DB schema must match the 27 tables in `app/models/` and `docs/DB_SCHEMA.md`.
- RBAC enforces 3 active roles: `admin`, `teacher`, `student`. Legacy roles (`hos`, `hop`, `mentor`) are rejected with HTTP 403 `ROLE_DEPRECATED`.

## Explicitly Out of Scope Right Now
- Message queue (RabbitMQ/SQS) for concurrent classroom load
- Vector DB / FAISS / pgvector for similarity search at scale
- Multi-college / multi-tenant schema
- GPU provisioning or edge device protocols
These are real Phase 2 needs once there's an actual second classroom or college — not now.

## File/Naming Conventions
snake_case for all Python files, functions, and DB fields.

---

## Agent Response Convention

After completing any task in this module, always end your response with this block:

**Built:** [1–2 sentences — what was just implemented or changed in `backend/`]  
**Next:** [1–2 specific actionable next steps for this module]

Keep it short. One short paragraph maximum per section. No long summaries unless the user explicitly asks for one.
