# VISTA — API Specification

> **Last Updated:** 2026-06-24
> **Status:** Complete — implemented in `backend/app/routes/`
> **Canonical source:** `docs/API_CONTRACT.md` (frozen Day 3)

---

## 1. API Architecture

- **Framework:** FastAPI
- **Base URL:** `http://127.0.0.1:8000`
- **Prefix:** `/api/v1/`
- **Auth:** `Authorization: Bearer <jwt>` on all endpoints except login
- **Content-Type:** `application/json` (except export which returns CSV)
- **Error format:** `{"error": {"code": "...", "message": "...", "details": {}}}`

---

## 2. Endpoint Summary

| # | Method | Endpoint | Auth | Role | Status |
|---|---|---|---|---|---|
| 1 | POST | `/api/v1/auth/login` | No | — | ✅ |
| 2 | POST | `/api/v1/auth/logout` | Yes | Any | ✅ |
| 3 | GET | `/api/v1/students` | Yes | Any | ✅ |
| 4 | GET | `/api/v1/students/{id}` | Yes | Any | ✅ |
| 5 | POST | `/api/v1/attendance/mark` | Yes | Any | ✅ (vision stub) |
| 6 | GET | `/api/v1/attendance/log` | Yes | Any | ✅ |
| 7 | PATCH | `/api/v1/attendance/{id}` | Yes | Any | ✅ |
| 8 | GET | `/api/v1/students/{id}/risk` | Yes | Any | ✅ |
| 9 | GET | `/api/v1/risk` | Yes | Any | ✅ |
| 10 | POST | `/api/v1/students/{id}/risk/recompute` | Yes | Admin | ✅ |
| 11 | GET | `/api/v1/export/report` | Yes | Any | ✅ (CSV only) |
| 12 | POST | `/api/v1/students/{id}/enroll` | Yes | Admin | ❌ Planned |
| 13 | GET | `/health` | No | — | ✅ |

---

## 3. Authentication Strategy

- JWT created on login with HS256 algorithm
- Payload: `{sub: user_id, role: "admin"|"teacher", iat, exp}`
- Expiry: 8 hours (one school day)
- Revocation: in-memory set (single-process pilot)
- Secret: `VISTA_JWT_SECRET` env var (default for dev only)

---

## 4. Authorization Strategy

| Guard | Function | Used By |
|---|---|---|
| `get_current_user` | Validates token, returns User object | All protected endpoints |
| `require_admin` | Checks `user.role == "admin"` | Risk recompute, enrollment |

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

```
routes/auth.py       → User authentication + token management
routes/students.py   → Student CRUD (read-only in pilot)
routes/attendance.py → Attendance marking + log + override
routes/risk.py       → Risk flag retrieval + recompute
routes/export.py     → Report generation (CSV)
```

Each route file:
- Defines its own `APIRouter` with prefix and tags
- Uses `Depends(get_db)` for database sessions
- Uses `Depends(get_current_user)` for auth
- Returns structured JSON matching API contract

---

## 7. Key Design Decisions

1. **Absent entries are derived, not stored** — `GET /attendance/log` diffs roster vs present records
2. **Liveness failure writes a row** — captures spoofing attempt data
3. **Unrecognized faces write NO row** — measured via test set, not prod logs
4. **Risk is read from DB, not computed on GET** — only recomputed on explicit POST
5. **Vision shim returns stub** — allows backend to run without vision module installed
