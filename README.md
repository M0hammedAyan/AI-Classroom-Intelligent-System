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
| Aryan Raj Singh | Backend — API, database, data |
| Sujal Agrahari | Frontend — dashboard, UX |

**Institution:** DRAIT, Bangalore | School of CSE | AIML Department

---

## Facial Pipeline (New Addition)

### ✅ Completed
- **End-to-end facial pipeline script** (`vista/vision/facial_pipeline.py`) with structured nested-loop architecture
- **Dataset support**: Reads 21 student subfolders from `dataset/` (reg numbers as labels)
- **Face Extraction**: InsightFace SCRFD detector + ArcFace R50 recognizer (buffalo_l model pack)
- **Data Preprocessing**: Uniform resize to 160×160 with edge-case handling (bbox clamping)
- **Data Augmentation**: Albumentations pipeline with 30 variants/face (HorizontalFlip, RandomBrightnessContrast, Rotate ±15°, GaussNoise)
- **Feature Extraction**: Batch processing through ArcFace R50 → 512-dim embeddings
- **Global Compilation**: Master arrays for ~21K images, embeddings, labels, metadata
- **Robust Error Handling**: Skips corrupted images, missing faces; detailed progress logging
- **Results Persistence**: Compressed `.npz` output with all arrays and metadata
- **Per-student breakdown**: Individual stats per student folder (faces detected, augmentations, embeddings)
- **Dependencies Added**: `albumentations>=1.4.0` to requirements.txt

### 📋 Todo
- [ ] Run pipeline on Python 3.11/3.12 (onnxruntime wheels not yet available for Python 3.14)
- [ ] Verify output shapes match expected (~21K samples)
- [ ] Integrate pipeline output with enrollment system (`vista/vision/enroll.py`)
- [ ] Add unit tests for each pipeline stage
- [ ] Validate face detection rate across all 21 students

### 🔮 Future Suggestions
- **Multi-face support**: Extend to process group photos (classroom attendance) using `recognize_all()`
- **Advanced augmentations**: Add CutMix, MixUp, or face-specific augmentations (eyes/mouth masking)
- **Quality assessment**: Integrate face quality scores (blur, pose, illumination) before augmentation
- **Distributed processing**: Use multiprocessing/ray for parallel image processing
- **Incremental updates**: Support adding new students without reprocessing entire dataset
- **Embedding visualization**: t-SNE/UMAP projection of 512-dim embeddings for cluster analysis
- **ONNX export**: Export ArcFace R50 to ONNX for faster inference in production
- **Pipeline monitoring**: Add Prometheus metrics for processing time, success rates, queue depth
