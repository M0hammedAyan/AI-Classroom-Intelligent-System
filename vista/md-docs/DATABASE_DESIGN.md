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
| role | TEXT | NOT NULL: admin/teacher |
| is_active | BOOLEAN | NOT NULL, DEFAULT true |
| last_login_at | TEXT | nullable |
| created_at | TEXT | NOT NULL |

---

## 4. Indexing Strategy

| Table | Index | Purpose |
|---|---|---|
| attendance | (student_id, session_date) | ML feature queries |
| attendance | (classroom_id, session_date) | Attendance log queries |
| scores | (student_id, date) | Score trend queries |
| risk_flags | (student_id, calculated_at DESC) | Latest risk per student |
| users | (email) UNIQUE | Login lookup |

---

## 5. Seed Data (Auto-generated on Startup)

- 1 classroom (CSE-3A)
- 2 users (admin + teacher)
- 5 students with realistic profiles
- 8 weeks of attendance data (varied patterns)
- 3 assessments per student
- Risk flags computed via ML engine on startup

---

## 6. Migration Strategy

- **Pilot:** Drop and recreate on schema changes (acceptable for dev)
- **Phase 2:** Alembic migrations for PostgreSQL
- **Data preservation:** Seed script is idempotent (checks `classroom.count > 0`)
