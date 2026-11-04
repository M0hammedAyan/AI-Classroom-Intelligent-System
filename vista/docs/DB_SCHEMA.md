# VISTA Database Schema

**Owner:** Backend Team  
**Status:** Initial Day 3 Baseline (6 tables) expanded to Full Production Schema (27 tables across 8 model files in `vista/backend/app/models/`).

**Engine:** PostgreSQL (production). SQLite default for local development via SQLAlchemy 2.0 ORM (`backend/app/db.py`).  
**Passwords:** bcrypt, cost factor ≥ 12. Never store plaintext.  
**Timestamps:** UTC timestamps stored as DateTime/TIMESTAMP (PostgreSQL) / ISO 8601 strings (SQLite).  
**IDs:** UUID primary keys for system entities; natural college roll numbers (`student_id`) for students.

---

## Architecture Overview: 27 Tables Across 8 Model Modules

| Model Module | Source File | Tables Defined |
|---|---|---|
| **Organization** | `models/organization.py` | `schools`, `departments`, `class_sections`, `subjects`, `mentor_assignments`, `teacher_subjects`, `access_requests` (7 tables) |
| **User** | `models/user.py` | `users` (1 table; 3 active roles: admin, teacher, student; legacy HOS/HOP/Mentor deprecated) |
| **Student** | `models/student.py` | `classrooms`, `students` (2 tables) |
| **Attendance & Risk** | `models/attendance.py` | `attendance`, `scores`, `risk_flags` (3 tables) |
| **Interventions** | `models/intervention.py` | `interventions` (1 table) |
| **Audit** | `models/audit.py` | `audit_logs` (1 table) |
| **Notifications** | `models/notification.py` | `notifications` (1 table) |
| **Academics & Timetable** | `models/timetable.py` | `timetable_slots`, `announcements`, `study_materials`, `assignments`, `assignment_submissions`, `semester_results`, `parent_contacts`, `parent_alerts` (8 tables) |

---

## Core Relationships

```
schools ──1──* departments ──1──* class_sections ──1──* students
departments ──1──* subjects
classrooms ──1──* students
students ──1──* attendance
students ──1──* scores
students ──1──* risk_flags
students ──1──* interventions
students ──1──* semester_results
students ──1──* parent_contacts ──1──* parent_alerts
users ──1──* mentor_assignments ──*──1 students
users ──1──* teacher_subjects ──*──1 subjects
users ──1──* access_requests
users ──1──* notifications
users ──1──* audit_logs
class_sections ──1──* timetable_slots
class_sections ──1──* assignments ──1──* assignment_submissions
```

---

## Table: `classrooms`

One row for the pilot classroom. The table exists now so the schema does not change in Phase 2.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `classroom_id` | TEXT | PK | Business key, e.g. `"CSE-3A"` |
| `name` | TEXT | NOT NULL | Human-readable label |

**Phase 2 note:** An `institution_id` FK would be added here for multi-college support. Not built now.

---

## Table: `students`

The enrolled student roster for the pilot classroom.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `student_id` | TEXT | PK | College roll number, e.g. `"CS22B001"` — used as the shared key by vision and ML modules |
| `name` | TEXT | NOT NULL | Full name |
| `class` | TEXT | NOT NULL | Display label, e.g. `"CSE-3A"` |
| `classroom_id` | TEXT | FK → `classrooms.classroom_id`, NOT NULL | Structured FK for queries |
| `embedding` | JSONB / TEXT | nullable | Face embedding vector (array of floats). NULL until vision enrollment runs. Written by `vision/` module, read by `match.py`. |
| `enrolled_at` | TIMESTAMP | nullable | NULL until face embedding is captured |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | False if student withdrawn |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT now() | Row creation time (UTC) |

**Phase 2 note:** A `department_id` or `institution_id` column would be added for multi-tenant support. Not built now.

**Note on `embedding`:** Stored as JSONB (PostgreSQL) or JSON text (SQLite) — at 20–30 students, brute-force cosine similarity over in-memory vectors is fast enough. Do not add pgvector or FAISS for the pilot.

---

## Table: `attendance`

One row per recognition event. Grows by roughly `students × sessions_per_week` rows per week.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `student_id` | TEXT | FK → `students.student_id`, nullable | Null if liveness failed with no match, or for future unrecognized-audit use |
| `classroom_id` | TEXT | FK → `classrooms.classroom_id`, NOT NULL | Which classroom |
| `session_date` | DATE | NOT NULL | Date of the class session |
| `timestamp` | TIMESTAMP | NOT NULL | Exact capture time (UTC) |
| `status` | TEXT | NOT NULL | `"present"`, `"absent"`, `"liveness_failed"` |
| `confidence` | FLOAT | nullable | Vision recognition confidence `[0.0, 1.0]`. Null for manually-entered absent records. |
| `is_manual_override` | BOOLEAN | NOT NULL, DEFAULT false | True if a teacher corrected this record |
| `override_note` | TEXT | nullable | Teacher's reason; null if not overridden |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT now() | |

**Status values in DB vs API:**
- `"present"` — matched + liveness passed
- `"liveness_failed"` — liveness check failed; `student_id` stores the candidate match ID (may be null if matching also failed)
- `"absent"` — manually entered by teacher override only; **absent entries are not auto-written by the recognition pipeline** — absence is derived at read time in `GET /attendance/log`

**Indexes:**
- `(student_id, session_date)` — per-student attendance queries and ML feature engineering
- `(classroom_id, session_date)` — classroom-day log queries

**Phase 2 note:** If multi-classroom reporting is added, `classroom_id` is already the FK needed. No schema change required.

---

## Table: `scores`

Academic assessment scores. Used by `ml/features.py` for score-trend calculation.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `student_id` | TEXT | FK → `students.student_id`, NOT NULL | |
| `subject` | TEXT | NOT NULL | Subject name |
| `score` | FLOAT | NOT NULL | Raw score |
| `max_score` | FLOAT | NOT NULL | Maximum possible score |
| `date` | DATE | NOT NULL | Assessment date |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT now() | |

**Pilot note:** Populated manually or via CSV import. No LMS integration in this phase.

**Index:** `(student_id, date)` — score-trend queries.

---

## Table: `risk_flags`

Stores every risk computation result, not just the latest snapshot. This lets the team observe risk trends over the pilot period without a schema change.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `student_id` | TEXT | FK → `students.student_id`, NOT NULL | |
| `risk_level` | TEXT | NOT NULL | `"low"`, `"medium"`, or `"high"` |
| `reasons` | JSONB / TEXT | NOT NULL | JSON array of strings from ML engine, e.g. `["Attendance dropped 20%", "Score declined"]` |
| `confidence` | TEXT | NOT NULL | `"high"`, `"moderate"`, or `"low"` — from ML engine output |
| `calculated_at` | TIMESTAMP | NOT NULL | When this computation ran (UTC) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT now() | |

**Querying latest per student:**
```sql
SELECT * FROM risk_flags
WHERE student_id = $1
ORDER BY calculated_at DESC
LIMIT 1;
```

**Index:** `(student_id, calculated_at DESC)` — makes latest-per-student reads fast.

**Note on `reasons`:** JSONB in PostgreSQL, JSON text in SQLite. Backend deserialises to a Python list before returning via API. Do not store as comma-separated string.

**Phase 2 note:** If a separate `risk_flags_history` table is introduced later, this table becomes the "latest snapshot" table (one row per student, upserted). Do not implement that now — storing all rows here is fine for the pilot.

---

## Table: `users`

Admin and teacher accounts. Not linked to `students`.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `name` | TEXT | NOT NULL | Display name |
| `email` | TEXT | UNIQUE, NOT NULL | Login identifier |
| `password_hash` | TEXT | NOT NULL | bcrypt hash, cost ≥ 12. Never store plaintext. |
| `role` | TEXT | NOT NULL | `"admin"`, `"teacher"`, or `"student"` (legacy `"hos"`, `"hop"`, `"mentor"` deprecated — rejected at login with 403 ROLE_DEPRECATED) |
| `school_id` | UUID | FK → `schools.id`, nullable | Assigned school for HOS/staff |
| `department_id` | UUID | FK → `departments.id`, nullable | Assigned department for HOP/staff |
| `theme_preference` | TEXT | DEFAULT 'light' | User UI theme ('light' or 'dark') |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | False = account disabled |
| `last_login_at` | TIMESTAMP | nullable | Updated on successful login |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT now() | |

---

## Production Scope Status

### Implemented in Current Codebase
- 27 SQLAlchemy models across 8 modules
- 3 active roles (Admin, Teacher, Student); legacy HOS/HOP/Mentor deprecated and rejected at login with 403 ROLE_DEPRECATED
- LMS score import (CSV upload and Moodle REST API integration in `routes/lms.py`)
- APScheduler periodic background jobs (`app/scheduler.py`)
- Full academic features: timetable slots, announcements, study materials, assignments, submissions, semester results, and parent contacts/alerts

### Future / Next Phase Scope
- pgvector / FAISS vector index for embedding search (exact cosine similarity sufficient for current class sizes)
- Multi-institution SaaS tenancy (current system is scoped for single-institution multi-school deployment)
- Automated external SMS/email gateway dispatch for queued `parent_alerts`
