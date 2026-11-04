# VISTA — System Architecture

> **Last Updated:** 2026-06-24
> **Status:** Complete

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                                 │
│  React SPA (Vite + Tailwind v4) — Role-scoped portals:               │
│  Admin, Teacher, Student (legacy HOS/HOP/Mentor deprecated)         │
│  Communicates via REST API + WebSocket (/ws/dashboard)               │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │ HTTP/JSON & WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (FastAPI)                      │
│                                                                     │
│  14 Route Modules: academics, admin, attendance, auth, dashboards,  │
│  enroll, export, lms, mentor (deprecated), notifications, reports,  │
│  student_portal, students (122 registered routes)                   │
│  Background Services: scheduler.py (APScheduler), websocket.py,     │
│  audit.py, monitoring.py (Prometheus), cache.py (Redis/memory)      │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
                    ┌─────────────────┼──────────────────────────┐
                    │                 ▼                          ▼
                    │  ┌───────────────────────────┐  ┌──────────────────────┐
                    │  │ VISION MODULE             │  │ ML MODULE            │
                    │  │ vista/vision/             │  │ vista/ml/            │
                    │  │                           │  │                      │
                    │  │ recognize()               │  │ calculate_risk()     │
                    │  │ facial_pipeline.py        │  │ features.py          │
                    │  │ SCRFD + ArcFace R50       │  │ risk_engine.py       │
                    │  │ personal_classifier.py    │  │ explainer.py (SHAP)  │
                    │  │ tracker.py (IoU matching) │  │ train.py (XGBoost)   │
                    │  │ liveness.py (heuristics)  │  │ validate_uci.py      │
                    │  └───────────────────────────┘  └──────────────────────┘
                    │                   INTELLIGENCE LAYER                   │
                    └────────────────────────────────────────────────────────┘
                                               │
                                               ▼
                    ┌────────────────────────────────────────────────────────┐
                    │                   DATA LAYER                           │
                    │  PostgreSQL (prod) / SQLite (dev)                      │
                    │  27 Tables: access_requests, announcements,            │
                    │  assignment_submissions, assignments, attendance,      │
                    │  audit_logs, class_sections, classrooms, departments,   │
                    │  interventions, mentor_assignments, notifications,     │
                    │  parent_alerts, parent_contacts, risk_flags, schools,  │
                    │  scores, semester_results, students, study_materials,  │
                    │  subjects, teacher_subjects, timetable_slots, users    │
                    └────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Vision Module (`vista/vision/`)

| File | Responsibility | Input | Output |
|---|---|---|---|
| `detect.py` | Face detection via InsightFace SCRFD | Image path / numpy array | Bounding boxes + 5-point facial landmarks |
| `embed.py` | Feature extraction via ArcFace R50 | Aligned face crop | 512-dimensional normalized float vector |
| `match.py` | Cosine similarity gallery matching | Query vector + DB embeddings | Best match `student_id` + similarity score |
| `personal_classifier.py` | ResNet-50 PyTorch classifier fallback | Face crop (112x112) | Predicted student identity + softmax confidence |
| `tracker.py` | Multi-frame greedy IoU track manager | Bounding box sequence | Track IDs + active track histories |
| `liveness.py` | Heuristic anti-spoofing checks | Face crop | Boolean + heuristic metrics (texture, size) |
| `recognize.py` | Core recognition coordinator | Image path | List of match dictionaries |
| `facial_pipeline.py` | End-to-end processing script | Image / directory | Formatted attendance output and logs |
| `enroll.py` | Student enrollment pipeline | Image(s) + `student_id` | Stored 512-dim embedding in DB |

### 2.2 Backend Module (`vista/backend/app/`)

| Component | Responsibility |
|---|---|
| `main.py` | FastAPI application factory, middleware, CORS, router mounts, Prometheus metrics |
| `db.py` | SQLAlchemy database engine, session lifecycle, table initialization |
| `permissions.py` | RBAC access decorators and dependencies for 3 active roles (admin, teacher, student) |
| `scheduler.py` | APScheduler service for daily risk calculations and audit maintenance |
| `tasks.py` | Asynchronous job queues for background tasks |
| `websocket.py` | Connection manager and event broadcasting (`/ws/dashboard`) |
| `audit.py` | Structured audit logging into `audit_logs` table |
| `monitoring.py` | Prometheus metrics instrumentation and endpoint handlers |
| `cache.py` | Redis client with in-memory fallback for query caching |
| `routes/*.py` | 14 API route modules exposing 122 registered routes |
| `models/*.py` | 8 SQLAlchemy model files defining the 27 relational tables |

### 2.3 ML Module (`vista/ml/`)

| File | Responsibility |
|---|---|
| `features.py` | Feature extraction computing 8 engineered features + 3 override flags |
| `risk_engine.py` | Rule-based scoring + XGBoost classification + factor breakdowns |
| `explainer.py` | SHAP TreeExplainer wrapper for individual risk feature attribution |
| `train.py` | ML model training pipeline comparing XGBoost and Logistic Regression |
| `model.pkl` | Serialized trained XGBoost pipeline artifact |
| `data/generate_sample_data.py` | Synthetic student academic history generator |
| `data/student_data.csv` | Synthetic dataset for risk training and validation |
| `validate_uci.py` | Pipeline validation using UCI Student Performance benchmark |
| `tests/test_risk_engine.py` | 7 automated unit and integration tests |

### 2.4 Frontend Module (`vista/frontend/src/`)

| File / Directory | Responsibility |
|---|---|
| `api/client.js` | Axios API client configured with auth headers and error handling |
| `pages/` | Role-specific views for Admin, Teacher, and Student |
| `components/` | Reusable UI components (KPI cards, charts, modals, layout) |
| `App.jsx` | Client routing, role-based route protection, navigation shell |

---

## 3. Module Boundaries (Strict)

```
vision/ ──── DOES NOT import from backend/ or ml/
ml/     ──── DOES NOT import from vision/ or frontend/
backend/ ─── IMPORTS vision.facial_pipeline / recognize and ml.risk_engine
frontend/ ── COMMUNICATES only via HTTP API & WebSocket (never imports Python)
```

### Fixed Entry Points (signatures never change)

```python
# vision/recognize.py
def recognize(image_path: str) -> list[dict]:
    # Returns: [{student_id: str|None, confidence: float, liveness_passed: bool}]

# ml/risk_engine.py
def calculate_risk(student_id: str) -> dict:
    # Returns: {risk_level, risk_score, reasons, recommendations, confidence, ...}

def calculate_risk_from_metrics(metrics: StudentMetrics) -> dict:
    # Same output, but accepts pre-built metrics (no DB call)
```

---

## 4. Security Architecture

| Layer | Mechanism |
|---|---|
| Authentication | JWT (HS256), 8-hour expiry default |
| Password storage | bcrypt, cost factor ≥ 12 |
| Authorization | Role-based (admin, teacher, student) via `require_role` / `permissions.py`; legacy roles HOS/HOP/Mentor deprecated |
| Token revocation | In-memory blocklist / Redis |
| CORS | Configurable whitelist (`http://localhost:5173`, `http://localhost:3000`) |
| Input validation | Pydantic v2 schemas across all routes |
| File handling | Temp upload files sanitized and cleaned up post-inference |

---

## 5. Scalability Considerations (Phase 2+)

| Concern | Current (Pilot) | Production Target |
|---|---|---|
| Students | 30 (brute-force cosine sim) | pgvector / FAISS for >100 |
| Concurrent users | 5 | Gunicorn workers + connection pooling |
| Video processing | Not supported | RTSP stream + ByteTrack |
| Database | SQLite | PostgreSQL |
| Deployment | Single process | Docker Compose → Kubernetes |
| Caching | None | Redis for embeddings + session |
