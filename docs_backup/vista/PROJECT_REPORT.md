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
│  Views assigned students + their subjects + teachers │
│  Cannot create users                                 │
│  Requests access via approval workflow               │
├─────────────────────────────────────────────────────┤
│  TEACHER                                             │
│  Creates subject groups, manages own classes         │
│  Marks attendance, manages scores                    │
│  Requests access via approval workflow               │
└─────────────────────────────────────────────────────┘
```

### Organization Hierarchy

```
Institution
  └── School (e.g., School of CS, School of Mechanical)
        └── Department (e.g., AIML, CSE, ISE, ME, Civil)
              └── Class Section (e.g., AIML-3A, CSE-2B)
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

### Computer Vision
| Technology | Purpose |
|---|---|
| InsightFace | Unified face analysis framework |
| SCRFD | Face detection (finds faces in images) |
| ArcFace R50 | Face embedding (512-dim identity vectors) |
| Cosine Similarity | Identity matching |
| ByteTrack | Multi-face temporal tracking |
| MiniFASNet | Anti-spoofing / liveness detection |
| OpenCV | Image processing |
| ONNX Runtime | Model inference on CPU |

### Machine Learning
| Technology | Purpose |
|---|---|
| XGBoost | Risk classification (F1 = 0.957) |
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
| Tailwind CSS | Utility-first styling |
| Custom CSS | Component-specific styles |

### Deployment
| Technology | Purpose |
|---|---|
| Docker | Containerization |
| Docker Compose | Multi-service orchestration |
| Nginx | Reverse proxy + static serving |
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
│  42 API Endpoints │ JWT Auth │ RBAC │ WebSocket │ Scheduler     │
└─────────┬──────────────────────────────────┬───────────────────┘
          │                                  │
          ▼                                  ▼
┌──────────────────────┐      ┌──────────────────────────────────┐
│   VISION MODULE      │      │      ML MODULE                    │
│   InsightFace        │      │   XGBoost + SHAP                  │
│   ArcFace R50        │      │   8 Engineered Features           │
│   ByteTrack          │      │   Rule-Based + ML Scoring         │
└──────────────────────┘      └──────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   DATABASE            │
                    │   13 Tables           │
                    │   SQLite / PostgreSQL │
                    └──────────────────────┘
```

---

## 6. API Summary (42 Endpoints)

| Category | Endpoints | Purpose |
|---|---|---|
| Authentication | 2 | Login, Logout |
| Students | 2 | List, Detail |
| Attendance | 5 | Mark, Mark-Batch, Mark-Video, Log, Stats |
| Risk | 5 | View, List, Recompute, Recompute-All, Explain (SHAP) |
| Enrollment | 1 | Face registration |
| Export | 1 | CSV + PDF reports |
| LMS | 4 | View scores, Add score, Import CSV, Moodle Sync |
| Admin | 15 | User CRUD, Schools, Departments, Assignments, Requests |
| WebSocket | 1 | Real-time dashboard updates |
| Health | 1 | System status check |

---

## 7. Database Schema (13 Tables)

| Table | Purpose |
|---|---|
| users | All system users (admin, HOS, HOP, mentor, teacher) |
| schools | College schools (CS, Mechanical, etc.) |
| departments | Departments within schools (AIML, CSE, etc.) |
| class_sections | Class groups (AIML-3A, CSE-2B) |
| subjects | Academic subjects |
| students | Enrolled students with face embeddings |
| classrooms | Physical classroom mapping |
| attendance | Per-session attendance records |
| scores | Academic assessment scores |
| risk_flags | Risk computation history |
| mentor_assignments | Mentor → student mappings |
| teacher_subjects | Teacher → subject + class mappings |
| access_requests | Approval workflow records |

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
| Total API endpoints | 42 |
| Database tables | 13 |
| Frontend pages | 8 |
| ML features | 8 |
| Vision pipeline stages | 5 (detect → embed → match → liveness → track) |
| User roles | 5 (admin, HOS, HOP, mentor, teacher) |
| Test cases | 13 (7 ML + 6 vision) |
| Model accuracy | 95% (XGBoost) |
| Lines of Python | ~3,000+ |
| Lines of JavaScript | ~2,000+ |
