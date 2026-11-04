# VISTA — Project Report

## Visual Intelligence System for Tracking and Analysis

---

## 1. Project Overview

VISTA is an AI-powered Academic Intelligence Platform that automates classroom attendance using face recognition and predicts student academic risk using machine learning. Unlike traditional attendance systems that only record presence, VISTA answers critical questions:

- Which students are academically at risk?
- Why are they at risk?
- What interventions should educators take?
- How is student performance changing over time?

---

## 2. What VISTA Does

| Capability | Description |
|---|---|
| **Automated Attendance** | Camera captures classroom image → AI detects and identifies student faces → attendance marked automatically |
| **Multi-Face Detection** | Single group photo identifies ALL students simultaneously |
| **Academic Risk Prediction** | Classifies students as LOW / MEDIUM / HIGH risk based on attendance + academic patterns |
| **Explainable AI (SHAP)** | Every prediction comes with reasons explaining WHY a student is at risk |
| **Actionable Recommendations** | Tells educators exactly what to do (e.g., "Schedule counselling", "Notify HOD") |
| **Real-Time Dashboard** | Live attendance stats, risk flags, trend charts, and analytics |
| **LMS Integration** | Import scores from CSV or sync directly from Moodle |
| **PDF/CSV Reports** | Export attendance reports for any date range |
| **Multi-Face Tracking** | ByteTrack-based temporal tracking to confirm identity over video frames |
| **WebSocket Updates** | Real-time push notifications when attendance is marked |

---

## 3. Access Control System (RBAC)

VISTA implements a hierarchical Role-Based Access Control system mirroring a real college structure:

```
┌─────────────────────────────────────────────────────┐
│  ADMIN (Full Control)                                │
│  Creates all users, manages entire system            │
├─────────────────────────────────────────────────────┤
│  HOS (Head of School)                                │
│  Full control within their school                    │
│  Can create: HOP, Mentor, Teacher                    │
├─────────────────────────────────────────────────────┤
│  HOP / HOD (Head of Department)                      │
│  Full control within their department                │
│  Can create: Mentor, Teacher                         │
│  Approves access requests                            │
├─────────────────────────────────────────────────────┤
│  MENTOR                                              │
│  Views assigned students + watchlist + interventions │
│  Cannot create users; requests access via workflow   │
├─────────────────────────────────────────────────────┤
│  TEACHER                                             │
│  Creates subject groups, manages own classes         │
│  Marks attendance, manages scores, assignments       │
├─────────────────────────────────────────────────────┤
│  STUDENT                                             │
│  Personal portal: timetable, attendance by subject,  │
│  scores, materials, extracurriculars, notifications  │
└─────────────────────────────────────────────────────┘
```

### Organization Hierarchy

```
Institution
  └── School (e.g., School of CS, School of Mechanical)
        └── Department (e.g., AIML, CSE, ISE, ME, Civil)
              └── Class Section (e.g., AIML-4A, CSE-2B)
                    └── Students (auto-assigned on admission)
```

### Permission Features

- **Role-based defaults** — each role gets standard permissions automatically
- **Custom permissions** — Admin/HOS can grant extra access to any user
- **Scoped access** — users only see data within their school/department
- **Approval workflow** — teachers/mentors request access → HOP/HOS approves
- **Mentor assignment** — specific students assigned to specific mentors
- **Teacher-subject mapping** — teachers linked to their subjects + classes

---

## 4. Tech Stack

#### Computer Vision
| Technology | Purpose |
|---|---|
| InsightFace | Unified face analysis framework |
| SCRFD | Face detection (finds faces in images) |
| ArcFace R50 | Face embedding (512-dim identity vectors) |
| Cosine Similarity | Identity matching (threshold 0.55) |
| Personal Classifier | ResNet-50 PyTorch checkpoint runtime adapter |
| ByteTrack-style Tracker | Multi-face temporal tracking (IoU greedy association, without Kalman filter) |
| Heuristic Liveness | Anti-spoofing via Laplacian variance, size, detection confidence (deep learning liveness planned) |
| OpenCV | Image processing |
| ONNX Runtime | Model inference on CPU |

### Machine Learning
| Technology | Purpose |
|---|---|
| XGBoost | Risk classification (F1 = 0.957 on synthetic data) |
| Logistic Regression | Baseline model comparison |
| SHAP (TreeExplainer) | Per-prediction explainability |
| scikit-learn | Training pipeline, evaluation |
| pandas / numpy | Data processing |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI | Async REST API framework |
| SQLAlchemy | ORM (database models) |
| SQLite / PostgreSQL | Database (dev / production) |
| PyJWT | JWT authentication |
| bcrypt | Password hashing |
| APScheduler | Scheduled background tasks |
| WebSocket | Real-time push updates |
| ReportLab | PDF report generation |

### Frontend
| Technology | Purpose |
|---|---|
| React 18 | UI component framework |
| Vite 5 | Build tool + dev server |
| React Router 6 | Client-side routing |
| Tailwind CSS v4 | Utility-first styling |
| Custom CSS | Component-specific styles |

### Deployment
| Technology | Purpose |
|---|---|
| Docker | Containerization |
| Docker Compose | Multi-service orchestration |
| Nginx | Reverse proxy + static serving (in frontend container) |
| PostgreSQL 16 | Production database |

---

## 5. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                      │
│  Login │ Dashboard │ Attendance │ Risk │ LMS │ Enroll │ Admin   │
└──────────────────────────────┬─────────────────────────────────┘
                               │ REST API + WebSocket
                               ▼
┌────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                            │
│  122 Routes (114 API) │ JWT Auth │ 3-Role RBAC │ WebSocket │
└─────────┬──────────────────────────────────┬───────────────────┘
          │                                  │
          ▼                                  ▼
┌──────────────────────┐      ┌──────────────────────────────────┐
│   VISION MODULE      │      │      ML MODULE                    │
│   InsightFace + R50  │      │   XGBoost + SHAP                  │
│   Personal ResNet-50 │      │   8 Engineered Features           │
│   ByteTrack IoU      │      │   Rule-Based + ML Scoring         │
└──────────────────────┘      └──────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   DATABASE            │
                    │   27 Tables           │
                    │   SQLite / PostgreSQL │
                    └──────────────────────┘
```

---

## 6. API Summary (122 Routes / 114 API Endpoints)

| Category / Module | Endpoints | Purpose |
|---|---|---|
| Admin (`/api/v1/admin`) | 29 | User CRUD, org tree, schools, depts, classes, subjects, mentor/teacher assignments, access requests, audit logs, CSV import |
| Academics (`/api/v1`) | 23 | Timetable, semester results, announcements, study materials, assignments, submissions, parent alerts |
| Attendance (`/api/v1/attendance`) | 8 | Mark, mark-batch, mark-video, log, manual override, stats, patch, subject breakdown |
| Student Portal (`/api/v1/student-portal`) | 10 | Personal dashboard, attendance, scores, timetable, subjects, extracurriculars, profile |
| Auth (`/api/v1/auth`) | 7 | Login, logout, get me, change password, profile update, theme update |
| Dashboards (`/api/v1/dashboard`) | 7 | Admin, HOS, HOP, teacher dashboards + attendance/risk/subject charts |
| ~~Mentor (`/api/v1/mentor`)~~ | *Deprecated* | Legacy mentor endpoints (deprecated in 3-role production runtime) |
| Risk (`/api/v1`) | 5 | Get student risk, list risk, recompute, recompute-all, SHAP explain |
| LMS (`/api/v1/lms`) | 4 | List scores, add score, CSV score import, Moodle API sync |
| Notifications (`/api/v1/notifications`) | 4 | List notifications, unread count, mark read, mark all read |
| Students (`/api/v1/students`) | 3 | List students, get student detail, academic record |
| Enrollment (`/api/v1/students`) | 2 | Single enrollment, bulk enrollment |
| Export (`/api/v1/export`) | 1 | CSV and PDF attendance report matrix |
| Reports (`/api/v1/reports`) | 1 | Comprehensive student PDF report |
| Core (`/`) | 4 | `/health`, `/metrics`, `/metrics/json`, `/ws/dashboard` (WebSocket) |

---

## 7. Database Schema (27 Tables)

| Table | Purpose |
|---|---|
| users | All system users across 3 active roles (admin, teacher, student; legacy roles deprecated) |
| schools | Academic schools |
| departments | Departments within schools |
| class_sections | Class groups / sections |
| subjects | Academic curriculum subjects |
| students | Enrolled students with face embeddings |
| classrooms | Physical classroom mapping |
| attendance | Per-session attendance records with confidence |
| scores | Academic assessment scores |
| risk_flags | Risk computation history and recommendations |
| mentor_assignments | Mentor → student mappings |
| teacher_subjects | Teacher → subject + class section mappings |
| access_requests | Approval workflow records |
| interventions | Mentoring intervention tracking |
| audit_logs | System-wide audit trail |
| notifications | In-app user notifications |
| timetable_slots | Weekly schedule slots |
| announcements | Scoped broadcast notices |
| study_materials | Downloadable academic materials |
| assignments | Course assignments |
| assignment_submissions | Student assignment submissions and grading |
| semester_results | End-semester grading records |
| parent_contacts | Student parent/guardian contacts |
| parent_alerts | Queued parent notifications (SMS/email delivery planned) |

---

## 8. ML Model Performance

| Model | Accuracy | Macro F1 | Status |
|---|---|---|---|
| XGBoost (100 trees) | 95% | 0.957 | ✅ Production |
| Logistic Regression | 93% | 0.94 | Baseline |
| Rule-Based Engine | — | — | ✅ Fallback |

### Risk Classification

| Level | Score Range | Meaning |
|---|---|---|
| LOW | 0–39 | Student performing normally |
| MEDIUM | 40–69 | Warning signals — intervention recommended |
| HIGH | 70–100 | Academic distress — immediate action required |

### Features Used (8)
1. Overall attendance percentage
2. Attendance drop (recent vs earlier)
3. Internal marks average
4. Marks decline from peak
5. Assignment completion rate
6. Consecutive absence count
7. Performance trend (improving/stable/declining)
8. Engagement score (composite)

---

## 9. Key Differentiators

| Feature | Traditional Systems | VISTA |
|---|---|---|
| Attendance marking | Manual / biometric | AI face recognition |
| Multi-student | One at a time | All at once (group photo) |
| Analytics | None | Full risk prediction |
| Explainability | None | SHAP-based reasons |
| Recommendations | None | Actionable suggestions |
| Real-time | None | WebSocket push |
| Access control | Single role | 5-level hierarchy |
| LMS integration | None | CSV + Moodle API |

---

## 10. Research References

| Paper | Year | Used For |
|---|---|---|
| ArcFace (Deng et al.) | CVPR 2019 | Face recognition embeddings |
| ByteTrack (Zhang et al.) | ECCV 2022 | Multi-object tracking |
| XGBoost (Chen & Guestrin) | KDD 2016 | Risk classification |
| SHAP (Lundberg & Lee) | NeurIPS 2017 | Model explainability |
| InsightFace | 2019+ | Face detection + analysis toolkit |
| Deep OC-SORT | 2023 | Observation-centric tracking (roadmap) |

---

## 11. How to Run

```bash
# Backend (from project root)
python -m uvicorn vista.backend.app.main:app --host 127.0.0.1 --port 8002

# Frontend (separate terminal)
cd vista/frontend
npm run dev

# Open browser: http://localhost:5173
# Login: admin@vista.local / admin123
```

---

## 12. Project Statistics

| Metric | Value |
|---|---|
| Total API endpoints | 122 (114 API + 4 system + 4 docs) |
| Database tables | 24 |
| Frontend pages | 20+ |
| ML features | 8 engineered features (5 in pipeline) |
| Vision pipeline stages | 5 (detect → crop → match/classify → liveness → track) |
| User roles | 3 active roles (admin, teacher, student; HOS/HOP/mentor deprecated) |
| Automated test cases | 14 (7 ML + 7 vision) |
| Model performance | XGBoost macro F1 = 0.957 (synthetic validation); Face classifier test acc = 90.10% (split B NPZ) |
| Lines of Python | ~6,000+ |
| Lines of JavaScript | ~3,000+ |
