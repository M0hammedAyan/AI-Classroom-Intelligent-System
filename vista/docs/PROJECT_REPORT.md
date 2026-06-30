# VISTA — Project Technical Report

> **Version:** 1.0 (Pilot Ready)
> **Date:** June 30, 2026
> **Team:** Mohammed Ayan, Saheel Pradhan, Sujal Agrahari, Aryan Raj Singh
> **Institution:** DSATM, Bangalore (School of CSE, AIML Department)

---

## 1. Executive Summary

VISTA (Visual Intelligence for Student Tracking & Analytics) is an AI-powered academic
monitoring system that combines face recognition attendance with machine learning risk
prediction to identify at-risk students before they fail.

**Key Results:**
- Face recognition: 100% accuracy on real student photos (14 images, 2 students)
- Risk engine: F1 = 0.957 on synthetic validation pipeline
- System: 85+ API endpoints, 6-role RBAC, real-time WebSocket updates
- Frontend: Enterprise-grade React dashboard with dark/light themes
- 24 database tables, 50+ features, role-specific dashboards
- Zero-warning production build, Docker-ready deployment

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    VISTA Platform                      │
├──────────┬──────────┬──────────┬────────────────────┤
│  Vision  │    ML    │ Backend  │     Frontend        │
│ Pipeline │  Engine  │   API    │    Dashboard        │
├──────────┼──────────┼──────────┼────────────────────┤
│InsightFace│ XGBoost │ FastAPI  │   React + Vite     │
│ ArcFace  │  SHAP   │ SQLite   │   Design System    │
│  SCRFD   │ Rules   │   JWT    │   WebSocket RT     │
└──────────┴──────────┴──────────┴────────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Face Detection | SCRFD (InsightFace) | Multi-face detection in classroom photos |
| Face Recognition | ArcFace R50 | 512-dim embedding extraction + cosine matching |
| Risk Prediction | XGBoost + Rule Engine | Hybrid ML + heuristic risk scoring |
| Explainability | SHAP TreeExplainer | Per-feature contribution visualization |
| Backend | FastAPI (Python 3.11+) | REST API + WebSocket + async |
| Database | SQLite (dev) / PostgreSQL (prod) | 24 tables, full relational schema |
| Auth | JWT (HS256, 8hr expiry) | Role-based access, rate limiting |
| Frontend | React 18 + Vite | SPA, enterprise design system |
| Styling | Custom CSS Design System | Inter font, 8pt grid, dark/light themes |
| Infra | Docker Compose | Postgres + Redis + Gunicorn + Celery + Nginx |
| Monitoring | Prometheus + JSON logging | /metrics endpoint, structured logs |

---

## 3. Features (Complete List)

### Core AI Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | Face Attendance (Single) | Upload photo → detect face → match → mark present |
| 2 | Face Attendance (Batch) | Classroom group photo → detect ALL faces → mark all |
| 3 | Face Attendance (Video) | Frame-by-frame with ByteTrack temporal consistency |
| 4 | Risk Prediction | XGBoost + 9 rule-based checks → LOW/MEDIUM/HIGH |
| 5 | SHAP Explainability | Per-feature contribution bars for each prediction |
| 6 | Auto Risk Alerts | HIGH risk triggers notifications to mentor + HOP |

### Academic Features

| # | Feature | Description |
|---|---------|-------------|
| 7 | Per-subject attendance | Track attendance by subject, not just overall |
| 8 | Internal marks entry | Per-subject scores with averages |
| 9 | Semester results | Final exam marks, grades, pass/fail |
| 10 | Timetable | Weekly class schedule per section |
| 11 | Assignments | Create → Submit → Grade workflow |
| 12 | Study materials | Upload/download PDFs, notes per subject |
| 13 | Announcements | Scoped notices (all/school/dept/class) |

### Platform Features

| # | Feature | Description |
|---|---------|-------------|
| 14 | 6-role RBAC | Admin, HOS, HOP, Mentor, Teacher, Student |
| 15 | Scoped access | Each role sees only their school/dept/class students |
| 16 | User creation hierarchy | Admin→HOS→HOP→Mentor/Teacher/Student |
| 17 | Subject management | HOS/HOP create subjects visible downstream |
| 18 | Bulk student CSV import | Upload CSV → creates student + login accounts |
| 19 | Bulk face enrollment | Multiple photos per student, batch processing |
| 20 | Mentor-student assignment | Map mentors to specific students |
| 21 | Teacher-subject-class assignment | Map teachers to subjects + classes |
| 22 | Organization tree (Admin) | Visual hierarchy: School→Dept→Class→Subject→User |
| 23 | Role-specific dashboards | Teacher, Mentor, Student each get tailored views |
| 24 | Class section management | HOP/HOS/Admin create classes within departments |

### Student Portal

| # | Feature | Description |
|---|---------|-------------|
| 22 | Student dashboard | Attendance %, scores, risk, at-a-glance |
| 23 | My Attendance (per-subject) | Subject-wise attendance breakdown |
| 24 | My Scores | Grouped by subject with averages |
| 25 | My Subjects | Subject list with teacher info |
| 26 | Profile edit | Name editable, USN editable ONCE |
| 27 | Extracurricular | Add/manage activities |
| 28 | Risk status | See own risk level with explanations |

### Communication & Alerts

| # | Feature | Description |
|---|---------|-------------|
| 29 | In-app notifications | Auto-generated on HIGH risk, bell + panel UI |
| 30 | Parent contacts | Store parent phone/email per student |
| 31 | Parent alerts (SMS/email) | Queue alerts for low attendance, high risk |
| 32 | Announcements | Broadcast from HOP/HOS/Admin to students |

### Reports & Export

| # | Feature | Description |
|---|---------|-------------|
| 33 | Student PDF report | Comprehensive downloadable report per student |
| 34 | Attendance CSV export | Classroom attendance for date range |
| 35 | Attendance PDF export | Formatted PDF with summary |

### Infrastructure

| # | Feature | Description |
|---|---------|-------------|
| 36 | Dark/Light theme | Ocean green accent dark mode, persisted per user |
| 37 | Password change | Self-service for all roles |
| 38 | Real-time WebSocket | Live attendance updates on dashboard |
| 39 | Prometheus monitoring | /metrics endpoint, request latency, error tracking |
| 40 | Audit logging | All admin actions logged with timestamp + IP |
| 41 | Rate limiting | Login brute-force protection (5 attempts/5min) |
| 42 | Secure headers | X-Frame-Options, HSTS, CSP-ready |
| 43 | Docker production | Compose with Postgres + Redis + Nginx |
| 44 | Zero-warning build | Clean Vite production build |
| 45 | Timetable seed data | 30 slots (6 periods × 5 days) with 6 subjects |
| 46 | Role-specific dashboards | Admin=org tree, Teacher=classes, Mentor=watchlist, Student=schedule |

---

## 4. Database Schema (24 Tables)

```
users, students, classrooms, schools, departments, class_sections,
subjects, attendance, scores, risk_flags, mentor_assignments,
teacher_subjects, access_requests, interventions, audit_logs,
notifications, timetable_slots, announcements, study_materials,
assignments, assignment_submissions, semester_results,
parent_contacts, parent_alerts
```

---

## 5. API Endpoints (70+)

### Auth (6)
- POST /auth/login, /auth/logout, /auth/change-password
- GET /auth/me, /auth/profile
- PATCH /auth/profile, /auth/theme

### Students (3)
- GET /students, /students/{id}
- Scoped by role automatically

### Attendance (7)
- POST /attendance/mark, /mark-batch, /mark-video
- GET /attendance/log, /attendance/stats, /attendance/by-subject/{id}
- PATCH /attendance/{id}

### Risk (5)
- GET /risk, /students/{id}/risk, /students/{id}/risk/explain
- POST /students/{id}/risk/recompute, /risk/recompute-all

### Admin (15+)
- CRUD users, schools, departments, subjects
- Assign mentors, teachers
- Access requests workflow
- Bulk student import, audit logs

### Academics (15+)
- CRUD timetable, announcements, assignments, materials
- Semester results (single + bulk)
- Assignment submission + grading
- Parent contacts + alerts

### Student Portal (8)
- GET dashboard, attendance, attendance/by-subject, scores, subjects, profile, extracurricular, risk
- PATCH profile
- PUT extracurricular

### Notifications (4)
- GET /notifications, /notifications/unread-count
- PATCH /notifications/{id}/read, /notifications/read-all

### Reports (1)
- GET /reports/student/{id}/pdf

### Export (1)
- GET /export/report (CSV + PDF)

---

## 6. ML Pipeline Details

### Risk Engine Architecture

```
Student Data → Feature Engineering → XGBoost Model → Rule Engine → Final Risk
                    ↓                      ↓              ↓
              9 features            probability      9 rule checks
                                    [0, 1]          override/boost
```

### Features (9)

| Feature | Source | Weight |
|---------|--------|--------|
| attendance_percentage | Attendance records | High |
| attendance_drop_percentage | Week-over-week change | High |
| consecutive_absences | Longest absent streak | Medium |
| internal_marks_average | Score records | High |
| marks_decline_percentage | Score trend | Medium |
| failed_subjects_count | Subjects < 40% | High |
| assignment_completion_rate | Submissions | Low |
| weeks_since_last_attendance | Recency | Medium |
| engagement_score | Composite | Low |

### Rule Engine (complements XGBoost)

| Rule | Condition | Action |
|------|-----------|--------|
| Chronic absence | >5 consecutive days | Force HIGH |
| Attendance critical | <50% | Force HIGH |
| Marks collapse | Average < 30% | Force HIGH |
| Attendance warning | <75% | Boost to MEDIUM min |
| Score decline | >20% drop | Boost by 0.15 |

### Model Performance (Synthetic Validation)

| Metric | Value |
|--------|-------|
| F1 Score | 0.957 |
| Precision | 0.96 |
| Recall | 0.95 |
| AUC-ROC | 0.98 |

**Note:** These metrics are on SYNTHETIC data generated to validate the pipeline.
Real-world accuracy will be measured during the pilot phase.

---

## 7. Vision Pipeline Details

### Architecture

```
Image → SCRFD Detection → Face Crop → ArcFace R50 → 512-dim Embedding
                                                          ↓
                                              Cosine Similarity Match
                                              (threshold: 0.45)
                                                          ↓
                                              Student ID + Confidence
```

### Performance (Real Data)

| Metric | Value | Test Set |
|--------|-------|----------|
| Detection accuracy | 100% | 14 photos (2 students) |
| Recognition accuracy | 100% | Saheel + Sujal |
| False Accept Rate | 0% | Tested with non-enrolled face (SRK photo) |
| Avg inference time | ~200ms | Per face on CPU |

### Multi-face Pipeline

1. SCRFD detects all faces in classroom image
2. Each face cropped + aligned
3. ArcFace extracts 512-dim embedding per face
4. Cosine similarity against enrolled gallery
5. Matches above threshold → marked present
6. ByteTrack temporal consistency (video mode)

---

## 8. Security

| Control | Implementation |
|---------|---------------|
| Authentication | JWT HS256, 8-hour expiry, token blocklist |
| Authorization | 6-role RBAC with hierarchical permissions |
| Rate limiting | 5 login attempts per 5 minutes per IP |
| Password storage | bcrypt (12 rounds) |
| Secure headers | X-Frame-Options, X-Content-Type-Options, XSS-Protection |
| Input validation | Pydantic models, magic byte validation for images |
| WebSocket auth | Token required as query param |
| Audit trail | All admin actions logged with user ID + IP |
| Data scope | Each role sees only authorized data |
| File upload | Size limits (5MB images, 50MB materials) |

---

## 9. Deployment

### Development
```bash
# Backend
cd vista/backend
uvicorn app.main:app --port 8002 --reload

# Frontend
cd vista/frontend
npm run dev
```

### Production (Docker)
```bash
cd vista
docker-compose up -d
```

Runs: PostgreSQL, Redis, Gunicorn (4 workers), Celery, Nginx (port 80)

---

## 10. Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@vista.local | admin123 |
| HOS | gowrishankar@vista.local | hos123 |
| HOP | ajayprakash@vista.local | hop123 |
| Teacher | kushal@vista.local | teacher123 |
| Mentor | rajeshwari@vista.local | mentor123 |
| Student | sujal@vista.local | student123 |
| Student | saheel@vista.local | student123 |
| Student | ayan@vista.local | student123 |
| Student | aryan@vista.local | student123 |

---

## 11. File Structure

```
vista/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app + middleware
│       ├── db.py                # Database engine + seed data
│       ├── models/              # 8 model files (24 tables)
│       ├── routes/              # 14 route files (70+ endpoints)
│       ├── monitoring.py        # Prometheus + logging
│       ├── permissions.py       # RBAC logic
│       ├── scheduler.py         # Periodic risk recomputation
│       └── websocket.py         # Real-time broadcast
├── frontend/
│   └── src/
│       ├── App.jsx              # Router + role-based nav
│       ├── layouts/             # RoleLayout with sidebar
│       ├── pages/               # 20+ page components
│       ├── components/          # NotificationBell, etc.
│       └── styles/              # Design system CSS
├── ml/
│   ├── risk_engine.py           # Main prediction pipeline
│   ├── features.py              # Feature engineering
│   ├── train.py                 # XGBoost training
│   └── data/                    # Sample data generator
├── vision/
│   ├── recognize.py             # Face recognition entry point
│   ├── enroll.py                # Face enrollment
│   ├── detector.py              # SCRFD face detection
│   ├── embedder.py              # ArcFace embedding
│   └── tracker.py               # ByteTrack multi-face
├── docs/
│   ├── IEEE_PAPER.md            # Research paper draft
│   └── PROJECT_REPORT.md        # This document
├── docker-compose.yml           # Production deployment
├── Dockerfile                   # Multi-stage build
├── gunicorn.conf.py            # WSGI config
└── PLANB.md                     # Roadmap document
```

---

## 12. What's Next (Pilot Phase)

1. Enroll 30 students (AIML 4A class)
2. Run daily attendance for 8 weeks
3. Compare with manual records
4. Validate risk predictions against mid-sem results
5. Collect real precision/recall/F1
6. Publish paper with real data

---

## 13. Final Metrics

| Metric | Value |
|--------|-------|
| Total features | 50+ |
| API endpoints | 85+ |
| Database tables | 24 |
| Frontend pages | 22 |
| Frontend components | 8 |
| User roles | 6 |
| CSS design system | 700+ lines |
| Production build | Zero warnings |
| Mobile responsive | Yes (768px + 480px breakpoints) |
| Dark/Light mode | Yes (ocean green accent) |
| Error handling | React ErrorBoundary + API error responses |
| Loading states | Shimmer skeletons |
| API caching | In-memory TTL cache |
| Documents | 7 (Report, Paper, PlanB, Pitch, Proposal, Consent, Demo Script) |
