# VISTA — AI Classroom Intelligent System

AI-powered academic monitoring: face recognition attendance + ML risk prediction + 6-role dashboard.

**Status:** Pilot-ready | **Features:** 50+ | **Endpoints:** 85+ | **Tables:** 24

---

## Quick Start

```bash
# Backend
cd vista/backend
pip install -r requirements.txt
uvicorn app.main:app --port 8002 --reload

# Frontend
cd vista/frontend
npm install && npm run dev
```

Login: `admin@vista.local` / `admin123`

---

## What VISTA Does

| Module | Function |
|--------|----------|
| **Vision** | Identify students from classroom photos (InsightFace ArcFace, 100% accuracy) |
| **ML** | Predict dropout risk from attendance + scores (XGBoost F1=0.957, SHAP) |
| **Platform** | 6-role dashboard for Admin, HOS, HOP, Mentor, Teacher, Student |
| **Alerts** | Auto-notify mentors + parents when student crosses HIGH risk |

---

## Key Features

- Face attendance (single/batch/video) — one photo marks entire class
- Per-subject attendance + marks tracking
- Risk prediction with SHAP explainability
- Timetable, assignments, study materials, announcements
- Parent SMS/email alerts
- Student PDF reports
- Dark/light mode for all users (ocean green accent dark theme)
- Real-time WebSocket dashboard updates
- Role-specific dashboards (Teacher, Mentor, Student, Admin)
- Organization tree management (Admin creates Schools → Depts → Classes → Subjects → Users)
- Docker production deployment
- Clean build (zero warnings)

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Vision | InsightFace (SCRFD + ArcFace R50) |
| ML | XGBoost + SHAP + Rule Engine |
| Backend | FastAPI, SQLAlchemy, JWT |
| Frontend | React 18 + Vite |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Infra | Docker Compose + Nginx + Redis + Celery |

---

## Roles

| Role | Access |
|------|--------|
| Admin | Everything — full system control |
| HOS | School-wide — create depts, users, subjects |
| HOP | Department — create users, manage subjects, view dept students |
| Teacher | Own classes — mark attendance, enter marks, assignments |
| Mentor | Assigned students — watchlist, interventions, risk tracking |
| Student | Own data — attendance, scores, risk, materials, timetable |

---

## Documentation

- [Technical Report](vista/docs/PROJECT_REPORT.md) — Full system documentation
- [IEEE Paper Draft](vista/docs/IEEE_PAPER.md) — Research paper
- [Plan B Roadmap](vista/PLANB.md) — Pilot → Publication → Product plan
- [Pitch Deck](vista/docs/PITCH_DECK.md) — 10-slide presentation for college management
- [Pilot Proposal](vista/docs/PILOT_PROPOSAL.md) — 1-page permission request
- [Consent Form](vista/docs/CONSENT_FORM.md) — Student face data collection consent
- [Demo Script](vista/docs/DEMO_SCRIPT.md) — 5-minute video recording guide

---

## Screenshots

Login as any role to see role-specific dashboards:
- **Admin**: Organization tree (Schools → Departments → Classes → Subjects → Users)
- **Teacher**: My subjects, at-risk students, quick actions (mark attendance, enter marks)
- **Mentor**: Watchlist, assigned students, risk alerts
- **Student**: Today's timetable, attendance heatmap, assignments, notices

---

## Team

| Member | Role |
|--------|------|
| Mohammed Ayan | Tech Lead — architecture, ML, paper |
| Saheel Pradhan | Vision — face recognition, enrollment |
| Sujal Agrahari | Backend — API, database, data |
| Aryan Raj Singh | Frontend — dashboard, UX |

**Institution:** DSATM, Bangalore | School of CSE | AIML Department
