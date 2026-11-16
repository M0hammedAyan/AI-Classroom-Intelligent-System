# VISTA Security Review — OWASP API Security Top 10 (2023)

> **Classification:** Confidential | **Date:** November 2026 | **Author:** VISTA Security Audit (Part 5)
>
> This document is the formal security review for the VISTA AI Classroom Intelligent System backend API (`vista/backend`). It assesses each item from the OWASP API Security Top 10 (2023 edition), documents the controls in place, and lists known gaps for future remediation.

---

## 1. API1:2023 — Broken Object Level Authorization (BOLA / IDOR)

| Status | Evidence |
|--------|----------|
| ✅ **Mitigated** | Central `auth_policy.py` helpers (`can_view_student`, `can_view_teacher`, `can_mutate_slot`) enforce object-level checks. Report routes, attendance routes, timetable mutation routes all call these helpers before returning data. |

**Controls:**
- `_authorize_student_report_access()` in `reports.py` checks role × ownership × class-assignment before returning any student data.
- `_authorize_teacher_report_access()` only allows admin or teacher (self).
- `_authorize_slot_mutation()` in `timetable.py` enforces teacher can only edit their own slots.
- Automated IDOR tests in `tests/test_security_part5.py::TestIDORPrevention`.

**Remaining gaps:**
- Student portal routes (`student_portal.py`) still use inline `current_user.id` comparisons — refactor to use `can_view_student()` in a future pass.

---

## 2. API2:2023 — Broken Authentication

| Status | Evidence |
|--------|----------|
| ✅ **Mitigated** | JWT-based authentication via `get_current_user` dependency. All non-public routes require a valid Bearer token. |

**Controls:**
- Tokens signed with `VISTA_JWT_SECRET` (env var). Warning logged at startup if default is used.
- `get_current_user` raises HTTP 401 for missing, expired, or invalid tokens.
- Passwords stored as `bcrypt` hashes (`password_hash` column).
- Login endpoint validates credentials before issuing tokens.

**Remaining gaps:**
- No token revocation / blacklist (logout is client-side only). Recommend Redis-based revocation list for production.
- JWT `exp` is set but refresh token rotation is not implemented.

---

## 3. API3:2023 — Broken Object Property Level Authorization

| Status | Evidence |
|--------|----------|
| ✅ **Mitigated** | Pydantic response models exclude internal fields. Forbidden field scan test (`TestForbiddenInternalFields`) verifies no `password_hash`, `face_embedding`, or JWT secrets appear in API responses. |

**Controls:**
- `Student` model never includes `face_embedding` in API responses.
- `User` model response does not include `password_hash`.
- `CaptureEvent` stores only SHA-256 hashes and metadata — no raw image bytes or embeddings.

**Remaining gaps:**
- Full response schema audit with `response_model=` on all routes not yet complete. Recommend adding explicit `response_model` Pydantic classes to all report and student endpoints.

---

## 4. API4:2023 — Unrestricted Resource Consumption

| Status | Evidence |
|--------|----------|
| ⚠️ **Partial** | In-process rate limiting implemented via `monitoring.py`. Report generation and capture endpoints do not have hard per-user rate limits. |

**Controls:**
- Request logging and latency metrics tracked per path.
- PDF generation is CPU-intensive; `reportlab` is synchronous but isolated per request.
- DB queries use `.limit()` on list endpoints (e.g., capture history uses `offset` + `limit` params).

**Remaining gaps:**
- No per-user rate limit on `/api/v1/reports/*/pdf` or `/api/v1/attendance/mark`. Add `slowapi` or token-bucket per-user limits in production.
- File upload size for face images should be validated (max ~2 MB per frame).

---

## 5. API5:2023 — Broken Function Level Authorization

| Status | Evidence |
|--------|----------|
| ✅ **Mitigated** | Role-based checks on every mutating endpoint. Route-level policy verified in `TestSecurityRouteInventory`. |

**Controls:**
- Admin-only actions: audit log access, cleanup jobs, slot management for all classes, student batch reassignment.
- Teacher actions: limited to their own subject/class assignments and their own timetable slots.
- Students: read-only access to own data only.
- `require_admin()` and `require_teacher_or_admin()` helpers in `auth_policy.py`.

**Remaining gaps:**
- Mentor role permissions not formally enumerated in `auth_policy.py` (currently handled inline in `reports.py` and `students.py`).

---

## 6. API6:2023 — Unrestricted Access to Sensitive Business Flows

| Status | Evidence |
|--------|----------|
| ⚠️ **Partial** | Attendance marking is gated by scheduled period window (10-minute grace) and teacher assignment. Extra classes require explicit `is_extra_class=True` + reason. |

**Controls:**
- `_resolve_active_slot_for_capture()` enforces that attendance can only be marked during scheduled periods.
- Out-of-period attendance raises HTTP 400 `OUTSIDE_SCHEDULED_PERIOD`.
- Duplicate attendance detection: same student × date × slot_id skips duplicate marks.
- CIE score editing is admin-only.

**Remaining gaps:**
- No detection of automated/bot replay attacks on attendance endpoint (e.g., same SHA-256 hash submitted repeatedly). Add deduplication by `image_sha256` within a time window.

---

## 7. API7:2023 — Server Side Request Forgery (SSRF)

| Status | Evidence |
|--------|----------|
| ✅ **Low Risk** | No URL-fetching functionality in the application. External requests are limited to Gemini API (via `llm_client.py`) with fixed `base_url`. |

**Controls:**
- No user-controlled URL inputs.
- Gemini API base URL is a compile-time constant, not user-controlled.

---

## 8. API8:2023 — Security Misconfiguration

| Status | Evidence |
|--------|----------|
| ✅ **Mitigated** | Security headers middleware, explicit CORS whitelist, JWT secret env-var warning. |

**Controls:**
- `add_security_headers` middleware sets:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: camera=(self), microphone=(), geolocation=()`
  - `Cache-Control: no-store`
- CORS restricted to `localhost:3000` and `localhost:5173` (Vite dev).
- FastAPI debug mode disabled in production via env-var check.

**Remaining gaps:**
- CORS origin list is hardcoded for dev; must be driven by env var in production (`VISTA_ALLOWED_ORIGINS`).
- No `Content-Security-Policy` header implemented yet. Recommend adding CSP with `script-src 'self'`.

---

## 9. API9:2023 — Improper Inventory Management

| Status | Evidence |
|--------|----------|
| ⚠️ **Partial** | All routes are registered through FastAPI's router and visible in `/openapi.json`. No shadow APIs. |

**Controls:**
- Route inventory test (`TestSecurityRouteInventory`) scans all registered routes and verifies they require authentication.
- All endpoints tagged in OpenAPI schema with version prefix `/api/v1/`.

**Remaining gaps:**
- `/metrics` endpoint exposes request counts and latency — should be protected or IP-restricted in production.
- No automatic retirement of deprecated endpoints (manual code review required).

---

## 10. API10:2023 — Unsafe Consumption of APIs

| Status | Evidence |
|--------|----------|
| ✅ **Mitigated** | Gemini API responses are parsed safely via Pydantic. LLM resilience layer (`llm_client.py`) handles 503/429 with circuit breaker and fallback models. |

**Controls:**
- LLM response text is not executed or eval'd; used only for text generation.
- HTTP 503 / MODEL_CAPACITY_EXHAUSTED triggers model fallback cascade.
- Exponential backoff with jitter respects `RetryInfo` delay.

---

## Summary Table

| # | Category | Status | Priority |
|---|----------|--------|----------|
| API1 | BOLA / IDOR | ✅ Mitigated | — |
| API2 | Broken Authentication | ✅ Mitigated | Token revocation (Medium) |
| API3 | Property Level AuthZ | ✅ Mitigated | Explicit response_model (Low) |
| API4 | Resource Consumption | ⚠️ Partial | Per-user rate limits (Medium) |
| API5 | Function Level AuthZ | ✅ Mitigated | Mentor role formalization (Low) |
| API6 | Business Flow | ⚠️ Partial | SHA-256 dedup window (Low) |
| API7 | SSRF | ✅ Low Risk | — |
| API8 | Misconfiguration | ✅ Mitigated | CSP header, env-driven CORS (Medium) |
| API9 | Inventory | ⚠️ Partial | Protect /metrics (Low) |
| API10 | Unsafe API Consumption | ✅ Mitigated | — |

---

## Critical Security Properties Verified

1. **No raw biometric data persisted** — `CaptureEvent` stores only SHA-256 hash + metadata. Never stores face images or embeddings. ✅
2. **No API key leakage** — Gemini API keys read from env, never logged or returned in responses. ✅
3. **Privacy isolation** — Chatbot history scoped to `current_user.id`. Student A cannot view Student B's conversations. ✅
4. **Server-side time** — All attendance timestamps resolved server-side in IST (`Asia/Kolkata`). No client-supplied timestamps trusted. ✅
5. **Audit trail** — Every report download, attendance mark, and slot mutation writes an `AuditLog` row. ✅

---

## Files Modified/Created in Part 5

| File | Change |
|------|--------|
| `vista/backend/app/auth_policy.py` | **New** — central authorization helpers |
| `vista/backend/app/routes/timetable.py` | Fixed `.dict()` → `.model_dump()` (Pydantic v2) |
| `tests/test_security_part5.py` | **New** — route inventory, forbidden fields, security headers, auth policy unit tests, IDOR tests |
| `vista/backend/SECURITY_REVIEW.md` | **New** (this document) |
