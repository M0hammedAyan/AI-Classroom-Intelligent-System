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

## Contract You Own (draft — finalize, don't silently change after Day 3)
| Endpoint | Method | Request | Response |
|---|---|---|---|
| `/api/auth/login` | POST | `{email, password}` | `{token, role}` |
| `/api/attendance/mark` | POST | `{image: base64, classroom_id}` | `{student_id, name, confidence, status}` |
| `/api/attendance/log` | GET | `?classroom_id&date` | `[{student_id, name, status, timestamp}]` |
| `/api/students/{id}/risk` | GET | — | `{student_id, risk_level, reasons}` |
| `/api/students` | GET | — | `[{student_id, name, class}]` |
| `/api/export/report` | GET | `?classroom_id&date_range` | PDF/CSV |

If you change a field name or shape after Day 3, that's a team sync, not a silent edit —
Frontend's mock data will silently break otherwise.

## Structure
- `app/routes/` — one file per resource (auth, attendance, students, risk)
- `app/models/` — DB models (student, attendance, user)
- `app/db.py`, `app/main.py`
- `mock_server/` — keep in sync with the real contract until Frontend has fully
  swapped over; don't let it drift

## Hard Rules
- DB schema must match `docs/DB_SCHEMA.md` exactly — that's what Member 4's risk engine
  reads from.
- Mock server must match the real contract shape, not a simplified version — otherwise
  Frontend integration in Week 7 breaks.

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
