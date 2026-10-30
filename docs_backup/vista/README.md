# VISTA — Visual Intelligence System for Tracking and Analysis

An AI-powered academic intelligence platform combining automated face recognition attendance with student risk prediction and explainable AI.

---

## Features

- **Face Recognition Attendance** — InsightFace (ArcFace R50 + SCRFD) detects and identifies students from classroom images
- **Multi-Face Detection** — Process group photos to mark multiple students at once
- **Academic Risk Prediction** — XGBoost + rule-based engine classifies students as LOW/MEDIUM/HIGH risk
- **SHAP Explainability** — Per-prediction feature contributions explain WHY a student is at risk
- **Real-Time Dashboard** — React SPA with attendance logs, risk flags, statistics, and WebSocket updates
- **LMS Integration** — Import scores from CSV or Moodle API
- **PDF/CSV Export** — Attendance reports in both formats
- **ByteTrack Tracking** — Multi-face temporal tracking for video-based attendance

---

## Architecture

```
Camera/Image Upload
       │
       ▼
┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Vision Module  │────▶│  FastAPI Backend  │────▶│  React SPA   │
│  InsightFace    │     │  SQLAlchemy ORM   │     │  Vite + CSS  │
│  ArcFace R50    │     │  JWT Auth         │     │              │
│  ByteTrack      │     │  WebSocket        │     │  Dashboard   │
└─────────────────┘     └────────┬──────────┘     │  Risk Flags  │
                                 │                │  Enrollment  │
                        ┌────────▼──────────┐     │  Statistics  │
                        │    ML Module      │     └──────────────┘
                        │  XGBoost + SHAP   │
                        │  Rule Engine      │
                        │  8 Features       │
                        └───────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Docker & Docker Compose

### Backend

```bash
cd "D:\MY_Projects\Major Project\AI-Classroom-Intelligent-System"
pip install -r vista/requirements.txt
python -m uvicorn vista.backend.app.main:app --host 127.0.0.1 --port 8002
```

Backend runs at `http://127.0.0.1:8002`. API docs at `/docs`.

### Frontend

```bash
cd vista/frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` (or next available port).

### Demo Accounts

| Email | Password | Role |
|---|---|---|
| admin@vista.local | admin123 | Admin |
| teacher@vista.local | teacher123 | Teacher |

---

## API Endpoints (24 routes)

| Category | Endpoint | Method |
|---|---|---|
| Auth | /api/v1/auth/login | POST |
| Auth | /api/v1/auth/logout | POST |
| Students | /api/v1/students | GET |
| Students | /api/v1/students/{id} | GET |
| Attendance | /api/v1/attendance/mark | POST |
| Attendance | /api/v1/attendance/mark-batch | POST |
| Attendance | /api/v1/attendance/mark-video | POST |
| Attendance | /api/v1/attendance/log | GET |
| Attendance | /api/v1/attendance/stats | GET |
| Attendance | /api/v1/attendance/{id} | PATCH |
| Risk | /api/v1/risk | GET |
| Risk | /api/v1/risk/recompute-all | POST |
| Risk | /api/v1/students/{id}/risk | GET |
| Risk | /api/v1/students/{id}/risk/recompute | POST |
| Risk | /api/v1/students/{id}/risk/explain | GET |
| Enrollment | /api/v1/students/{id}/enroll | POST |
| Export | /api/v1/export/report | GET |
| LMS | /api/v1/lms/import-csv | POST |
| LMS | /api/v1/lms/sync-moodle | POST |
| WebSocket | /ws/dashboard | WS |
| Health | /health | GET |

---

## Project Structure

```
vista/
├── backend/app/          # FastAPI application
│   ├── routes/           # API endpoints (auth, attendance, risk, export, enroll, lms)
│   ├── models/           # SQLAlchemy ORM models
│   ├── db.py             # Database engine + seed data
│   ├── websocket.py      # Real-time WebSocket manager
│   ├── scheduler.py      # APScheduler cron jobs
│   └── main.py           # App entry point
├── frontend/src/         # React SPA
│   ├── pages/            # Login, Dashboard, AttendanceLog, RiskFlags, Enroll, TestRecognition, StudentDetail
│   ├── components/       # Layout, ShapChart
│   └── api/client.js     # Centralized API client
├── ml/                   # Machine Learning
│   ├── features.py       # 8 engineered features
│   ├── risk_engine.py    # Rule-based + XGBoost + SHAP
│   ├── explainer.py      # SHAP TreeExplainer integration
│   ├── train.py          # Model training pipeline
│   └── model.pkl         # Trained XGBoost (F1=0.957)
├── vision/               # Computer Vision
│   ├── detect.py         # SCRFD face detection
│   ├── embed.py          # ArcFace R50 embeddings
│   ├── match.py          # Cosine similarity matching
│   ├── liveness.py       # Anti-spoofing heuristics
│   ├── recognize.py      # Pipeline orchestrator
│   ├── enroll.py         # Face enrollment
│   └── tracker.py        # ByteTrack multi-face tracking
├── docs/                 # Contract documents (API, DB schema, specs)
├── md-docs/              # Architecture & planning documents
├── docker-compose.yml    # Docker deployment
├── Dockerfile            # Backend container
└── requirements.txt      # Python dependencies
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Face Detection | SCRFD (InsightFace) |
| Face Recognition | ArcFace R50 (512-dim embeddings) |
| Face Tracking | ByteTrack (IoU + Kalman) |
| Risk ML | XGBoost + Logistic Regression |
| Explainability | SHAP TreeExplainer |
| Backend | FastAPI + SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | React 18 + Vite |
| Auth | JWT (HS256, 8hr expiry) |
| Real-time | WebSocket |
| Deployment | Docker Compose |

---

## Running Tests

```bash
# ML tests (7 test cases)
python -m vista.ml.test_risk_engine

# Vision tests (6 test cases)
python -m vista.vision.test_recognize

# Frontend build check
cd vista/frontend && npm run build
```

---

## Docker Deployment

```bash
cd vista
docker compose up --build
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

---

## License

Academic project — AIML Final Year.
