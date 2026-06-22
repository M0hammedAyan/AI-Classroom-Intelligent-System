# VISTA API Contract — v1

**Owner:** Member 2 (Backend).  
**Status:** Frozen as of Day 3 — any change requires a team sync and a log entry in `INTEGRATION_LOG.md`. Do not silently edit this file.

**Base URL (dev):** `http://localhost:8000`  
**Versioning prefix:** `/api/v1/` — breaking changes increment to `/api/v2/`.  
**Auth:** `Authorization: Bearer <token>` on every endpoint except `POST /api/v1/auth/login`.  
**Content-Type:** `application/json` unless noted otherwise.

---

## Standard Error Response

All errors return the same envelope:

```json
{
  "error": {
    "code": "STUDENT_NOT_FOUND",
    "message": "No student with id S0042 exists.",
    "details": {}
  }
}
```

| Field | Type | Notes |
|---|---|---|
| `code` | string | Machine-readable constant (listed per endpoint below) |
| `message` | string | Human-readable description |
| `details` | object | Optional — e.g. validation field errors |

### HTTP Status Codes Used

| Status | Meaning |
|---|---|
| 200 | Success |
| 201 | Resource created |
| 400 | Bad request / validation failure |
| 401 | Missing or invalid token |
| 403 | Valid token, insufficient role |
| 404 | Resource not found |
| 500 | Internal server error |

---

## 1. Auth

### `POST /api/v1/auth/login`

Authenticate a user and receive a JWT. No auth header required.

**Request body:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `email` | string | yes | |
| `password` | string | yes | Plaintext over HTTPS — server compares against bcrypt hash |

**Success `200`:**

| Field | Type | Notes |
|---|---|---|
| `token` | string | JWT, expires in 8 hours |
| `role` | string | `"admin"` or `"teacher"` |
| `user_id` | string | UUID |
| `name` | string | Display name |

**Error codes:** `INVALID_CREDENTIALS` (401), `ACCOUNT_DISABLED` (403)

---

### `POST /api/v1/auth/logout`

Adds the current token to a server-side blocklist. Auth required (any role).

**Request body:** none  
**Success `200`:** `{ "message": "Logged out." }`

---

## 2. Students

### `GET /api/v1/students`

List enrolled students. Returns all students for the pilot classroom — no pagination needed at 20–30 students, but `page` / `page_size` params are accepted so the frontend doesn't need to change in Phase 2.

**Auth required:** yes (any role)  
**Query params:**

| Param | Type | Default | Notes |
|---|---|---|---|
| `page` | integer | 1 | 1-indexed |
| `page_size` | integer | 50 | Max 100 |

**Success `200`:**

```json
{
  "students": [ { ...Student } ],
  "total": 28,
  "page": 1,
  "page_size": 50
}
```

**Student object:**

| Field | Type | Notes |
|---|---|---|
| `student_id` | string | College roll number, e.g. `"CS22B001"` — same value used by vision and ML modules |
| `name` | string | Full name |
| `class` | string | Classroom identifier, e.g. `"CSE-3A"` |
| `enrolled_at` | string | ISO 8601 date |
| `is_active` | boolean | False if withdrawn |

---

### `GET /api/v1/students/{student_id}`

Fetch one student's profile.

**Auth required:** yes  
**Success `200`:** Single Student object.  
**Error codes:** `STUDENT_NOT_FOUND` (404)

---

## 3. Attendance

### `POST /api/v1/attendance/mark`

Accept a base64-encoded classroom image, call `vision.recognize()`, write the attendance record, and return the result. This is the only entry point for automated attendance.

**Auth required:** yes (teacher or admin)

**Request body:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `image` | string | yes | Base64-encoded JPEG or PNG, max 5 MB decoded |
| `classroom_id` | string | yes | e.g. `"CSE-3A"` |
| `session_date` | string | yes | ISO 8601 date `YYYY-MM-DD` |

**Backend logic (not part of the HTTP contract, documented here for Member 2):**
1. Decode image, save to a temp file.
2. Call `vision.recognize(image_path)` → `{ student_id, confidence, liveness_passed }`.
3. Determine `status` using the rules in the table below.
4. Write one row to `attendance`. See status rules.
5. Delete temp file. Return response.

**Status rules:**

| vision result | status written | attendance row written? |
|---|---|---|
| `liveness_passed = false` | `"liveness_failed"` | yes — `student_id` = candidate ID from vision (may be null if matching also failed), `confidence` stored |
| `student_id = null`, `liveness_passed = true` | `"unrecognized"` | no |
| `student_id` set, `liveness_passed = true` | `"present"` | yes |

**Success `200`:**

| Field | Type | Notes |
|---|---|---|
| `student_id` | string or null | Null if unrecognized or liveness failed with no match |
| `student_name` | string or null | Null if student_id is null |
| `status` | string | `"present"`, `"unrecognized"`, or `"liveness_failed"` |
| `confidence` | float | `[0.0, 1.0]` |
| `liveness_passed` | boolean | |
| `attendance_id` | integer or null | DB row id; null if no row was written |
| `marked_at` | string | ISO 8601 datetime UTC |

**Error codes:** `INVALID_IMAGE` (400), `NO_FACE_DETECTED` (400), `UPLOAD_TOO_LARGE` (400)

---

### `GET /api/v1/attendance/log`

Return the attendance log for a classroom and date. Absent students are **derived at read time** — the backend diffs the full student roster against present records and synthesizes absent entries for students with no row that day. No separate "close session" step required.

**Auth required:** yes  
**Query params:**

| Param | Type | Required | Default | Notes |
|---|---|---|---|---|
| `classroom_id` | string | yes | — | |
| `date` | string | yes | — | ISO 8601 date `YYYY-MM-DD` |

**Success `200`:**

```json
{
  "classroom_id": "CSE-3A",
  "date": "2026-06-21",
  "records": [ { ...AttendanceRecord } ],
  "total": 28
}
```

**AttendanceRecord object:**

| Field | Type | Notes |
|---|---|---|
| `attendance_id` | integer or null | Null for derived absent entries (no DB row) |
| `student_id` | string | |
| `student_name` | string | |
| `status` | string | `"present"`, `"absent"` (derived), `"liveness_failed"` |
| `confidence` | float or null | Null for absent or manual records |
| `marked_at` | string or null | Null for derived absent entries |
| `is_manual_override` | boolean | |

---

### `PATCH /api/v1/attendance/{attendance_id}`

Teacher manually corrects an existing attendance record.

**Auth required:** yes (teacher or admin)

**Request body:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `status` | string | yes | `"present"` or `"absent"` only |
| `note` | string | no | Reason for override, max 200 chars |

**Success `200`:** Updated AttendanceRecord object.  
**Error codes:** `ATTENDANCE_NOT_FOUND` (404), `INVALID_STATUS` (400)

---

## 4. Risk Flags

### `GET /api/v1/students/{student_id}/risk`

Return the most recent risk assessment for one student. Backend reads latest row from `risk_flags` table — does **not** recompute on every request.

**Auth required:** yes

**Success `200`:**

| Field | Type | Notes |
|---|---|---|
| `student_id` | string | |
| `student_name` | string | |
| `risk_level` | string | `"low"`, `"medium"`, or `"high"` |
| `reasons` | array of strings | From ML engine, e.g. `["Attendance dropped 20% in 3 weeks"]` |
| `confidence` | string | `"high"`, `"moderate"`, or `"low"` |
| `computed_at` | string | ISO 8601 datetime of last computation |

**Error codes:** `STUDENT_NOT_FOUND` (404), `RISK_NOT_COMPUTED` (404 — student exists but no risk row yet)

---

### `GET /api/v1/risk`

List latest risk flags for all students, optionally filtered by level.

**Auth required:** yes  
**Query params:**

| Param | Type | Default | Notes |
|---|---|---|---|
| `risk_level` | string | — | `"low"`, `"medium"`, or `"high"` |
| `page` | integer | 1 | |
| `page_size` | integer | 50 | Max 100 |

**Success `200`:**

```json
{
  "flags": [ { ...RiskFlag } ],
  "total": 28,
  "page": 1,
  "page_size": 50
}
```

RiskFlag schema same as `GET /students/{id}/risk` response.

---

### `POST /api/v1/students/{student_id}/risk/recompute`

Trigger a fresh risk computation for one student. Backend calls `ml.risk_engine.calculate_risk(student_id)`, writes a new row to `risk_flags`, and returns it.

**Auth required:** yes (admin only)  
**Request body:** none  
**Success `200`:** RiskFlag object.  
**Error codes:** `STUDENT_NOT_FOUND` (404)

---

## 5. Export

### `GET /api/v1/export/report`

Export an attendance report as CSV or PDF for a classroom and date range.

**Auth required:** yes (teacher or admin)  
**Query params:**

| Param | Type | Required | Notes |
|---|---|---|---|
| `classroom_id` | string | yes | |
| `from_date` | string | yes | ISO 8601 date |
| `to_date` | string | yes | ISO 8601 date |
| `format` | string | no | `"csv"` (default) or `"pdf"` |

**Success `200`:**
- Content-Type: `text/csv` or `application/pdf`
- Content-Disposition: `attachment; filename="attendance_CSE-3A_2026-06-01_2026-06-21.csv"`

**Error codes:** `INVALID_DATE_RANGE` (400 — `to_date` before `from_date`), `NO_DATA` (404)

---

## Out of Scope — Phase 2 Only

Do not build these in the pilot:

- Token refresh endpoint
- Webhooks or real-time push
- Multi-classroom routing
- Scheduled/automated risk recomputation
- Pagination on `GET /students` beyond the param stub already present

---

## Decisions Made (resolved from Open Questions)

These were reviewed and approved before the Day 3 freeze. Do not reopen without a team sync.

| # | Decision |
|---|---|
| 1 | Liveness failure logs a row with the candidate `student_id` (may be null) — does not mark attendance. Gives pilot spoofing-attempt data at zero extra cost. |
| 2 | Unrecognized faces write no DB row. False-reject rate is measured in `vision/test_recognize.py` against a labeled test set, not mined from prod logs. |
| 3 | Risk recompute is manual, admin-only. No scheduled automation in the pilot. |
| 4 | JWT expiry 8 hours, no refresh endpoint. One login per school day is sufficient. |
| 5 | Absent marking is derived at read time in `GET /attendance/log` — backend diffs roster vs present records. No "close session" endpoint needed. |
