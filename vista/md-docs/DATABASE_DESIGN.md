# VISTA — Database Design

> **Last Updated:** 2026-06-24
> **Status:** Complete — implemented in `backend/app/db.py` and `backend/app/models/`
> **Canonical source:** `docs/DB_SCHEMA.md` (frozen Day 3)

---

## 1. Database Engine

- **Development:** SQLite (file: `vista_dev.db`)
- **Production:** PostgreSQL
- **ORM:** SQLAlchemy 2.0 (same models work on both)
- **Migrations:** Manual (pilot); Alembic in Phase 2

---

## 2. Entity-Relationship Diagram

```
┌──────────────┐         ┌───────────────────────────┐
│  classrooms  │         │         students           │
│──────────────│         │───────────────────────────│
│ classroom_id │◄──1──*──│ classroom_id (FK)          │
│ name         │   PK    │ student_id (PK)            │
└──────────────┘         │ name                       │
                         │ class                      │
                         │ embedding (JSON, nullable) │
                         │ enrolled_at (nullable)     │
                         │ is_active                  │
                         │ created_at                 │
                         └─────┬───────────┬─────────┘
                               │           │
                    ┌──────────┘           └──────────┐
                    │                                 │
              ┌─────▼──────────┐            ┌────────▼─────────┐
              │   attendance   │            │     scores       │
              │────────────────│            │──────────────────│
              │ id (UUID, PK)  │            │ id (UUID, PK)    │
              │ student_id (FK)│            │ student_id (FK)  │
              │ classroom_id   │            │ subject          │
              │ session_date   │            │ score            │
              │ timestamp      │            │ max_score        │
              │ status         │            │ date             │
              │ confidence     │            │ created_at       │
              │ is_manual_     │            └──────────────────┘
              │   override     │
              │ override_note  │
              │ created_at     │
              └────────────────┘

              ┌────────────────────┐        ┌──────────────────┐
              │    risk_flags      │        │      users       │
              │────────────────────│        │──────────────────│
              │ id (UUID, PK)      │        │ id (UUID, PK)    │
              │ student_id (FK)    │        │ name             │
              │ risk_level         │        │ email (UNIQUE)   │
              │ reasons (JSON)     │        │ password_hash    │
              │ confidence         │        │ role             │
              │ calculated_at      │        │ is_active        │
              │ created_at         │        │ last_login_at    │
              └────────────────────┘        │ created_at       │
                                            └──────────────────┘
```

---

## 3. Table Specifications

### classrooms
| Column | Type | Constraints |
|---|---|---|
| classroom_id | TEXT | PK |
| name | TEXT | NOT NULL |

### students
| Column | Type | Constraints |
|---|---|---|
| student_id | TEXT | PK (college roll number) |
| name | TEXT | NOT NULL |
| class | TEXT | NOT NULL |
| classroom_id | TEXT | FK → classrooms, NOT NULL |
| embedding | TEXT/JSONB | nullable (JSON array of floats) |
| enrolled_at | TEXT | nullable |
| is_active | BOOLEAN | NOT NULL, DEFAULT true |
| created_at | TEXT | NOT NULL |

### attendance
| Column | Type | Constraints |
|---|---|---|
| id | TEXT (UUID) | PK |
| student_id | TEXT | FK → students, nullable |
| classroom_id | TEXT | FK → classrooms, NOT NULL |
| session_date | TEXT | NOT NULL (YYYY-MM-DD) |
| timestamp | TEXT | NOT NULL (ISO 8601) |
| status | TEXT | NOT NULL: present/absent/liveness_failed |
| confidence | FLOAT | nullable |
| is_manual_override | BOOLEAN | NOT NULL, DEFAULT false |
| override_note | TEXT | nullable |
| created_at | TEXT | NOT NULL |

### scores
| Column | Type | Constraints |
|---|---|---|
| id | TEXT (UUID) | PK |
| student_id | TEXT | FK → students, NOT NULL |
| subject | TEXT | NOT NULL |
| score | FLOAT | NOT NULL |
| max_score | FLOAT | NOT NULL |
| date | TEXT | NOT NULL (YYYY-MM-DD) |
| created_at | TEXT | NOT NULL |

### risk_flags
| Column | Type | Constraints |
|---|---|---|
| id | TEXT (UUID) | PK |
| student_id | TEXT | FK → students, NOT NULL |
| risk_level | TEXT | NOT NULL: low/medium/high |
| reasons | TEXT | NOT NULL (JSON array) |
| confidence | TEXT | NOT NULL: high/moderate/low |
| calculated_at | TEXT | NOT NULL |
| created_at | TEXT | NOT NULL |

### users
| Column | Type | Constraints |
|---|---|---|
| id | TEXT (UUID) | PK |
| name | TEXT | NOT NULL |
| email | TEXT | UNIQUE, NOT NULL |
| password_hash | TEXT | NOT NULL (bcrypt) |
| role | TEXT | NOT NULL: admin, teacher, student (legacy hos/hop/mentor deprecated) |
| is_active | BOOLEAN | NOT NULL, DEFAULT true |
| last_login_at | TEXT | nullable |
| created_at | TEXT | NOT NULL |

---

## 4. Full Production Schema (27 Tables across 8 Modules)

The complete backend database expands beyond the 6 pilot tables to 27 tables defined across 8 SQLAlchemy model files in `vista/backend/app/models/`:

| Model File | Table Name | Key Purpose |
|---|---|---|
| `organization.py` | `schools` | Academic institutions / faculties |
| `organization.py` | `departments` | Academic departments within schools |
| `organization.py` | `classrooms` | Physical or virtual classroom spaces |
| `organization.py` | `class_sections` | Student batch / section groupings |
| `organization.py` | `subjects` | Courses / academic subjects |
| `organization.py` | `teacher_subjects` | Mapping of teachers to taught subjects |
| `organization.py` | `access_requests` | Role/class permission escalation workflows |
| `user.py` | `users` | System user accounts and authentication credentials (3 active roles: admin, teacher, student) |
| `student.py` | `students` | Student records, roll numbers, and embedded face vectors |
| `student.py` | `semester_results` | Historical semester SGPA/CGPA and backlogs |
| `student.py` | `study_materials` | Uploaded academic documents and syllabi |
| `attendance.py` | `attendance` | Per-session facial and manual attendance logs |
| `attendance.py` | `scores` | Internal assessment and exam marks |
| `attendance.py` | `risk_flags` | Computed academic risk scores, levels, and factor JSON |
| `attendance.py` | `parent_alerts` | Automated communication log for parent absence notices |
| `timetable.py` | `timetable_slots` | Weekly scheduled periods by day, time, subject, room |
| `notification.py` | `notifications` | Role-targeted system notifications |
| `notification.py` | `announcements` | Institution and department-wide broadcast notices |
| `intervention.py` | `interventions` | Remedial counselling logs, action items, and outcomes |
| `intervention.py` | `mentor_assignments` | Student-to-faculty mentor mappings |
| `intervention.py` | `parent_contacts` | Directory of parent contact phone numbers and emails |
| `audit.py` | `audit_logs` | Security and access audit trail |
| `student.py` / LMS | `assignments` | LMS coursework and homework assignments |
| `student.py` / LMS | `assignment_submissions` | Student assignment file uploads and marks |
| coach module | `chat_messages` | AI Study Coach conversation history |
| `notification.py` | `notification_reads` | Per-user notification read status |
| `notification.py` | `notifications_legacy` | Legacy notification archive |

---

## 5. Indexing Strategy

| Table | Index | Purpose |
|---|---|---|
| attendance | (student_id, session_date) | ML feature queries |
| attendance | (classroom_id, session_date) | Attendance log queries |
| scores | (student_id, date) | Score trend queries |
| risk_flags | (student_id, calculated_at DESC) | Latest risk per student |
| users | (email) UNIQUE | Login lookup |
| audit_logs | (timestamp DESC, user_id) | Compliance review |

---

## 6. Seed Data (Auto-generated on Startup)

- Multi-tier institution structure (Dr. Ambedkar Institute of Technology, Bengaluru -> AIML Dept -> Sections)
- Seed users for 3 active roles (admin, teacher, student)
- Enrolled students with facial embeddings
- Timetable slots across 6 working days
- Multi-week attendance sessions with varied attendance patterns
- Historical assessment scores and seeded risk assessments

---

## 7. Migration Strategy

- **Development:** Automatic creation on startup via `Base.metadata.create_all(bind=engine)` in `db.py`
- **Production:** PostgreSQL with persistent storage volumes
- **Data preservation:** Seed script is idempotent (checks `User.count > 0` and `School.count > 0`)
