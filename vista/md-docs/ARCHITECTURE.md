# VISTA — System Architecture

> **Last Updated:** 2026-06-24
> **Status:** Complete

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                                 │
│  React SPA (Vite) — Login, Dashboard, AttendanceLog, RiskFlags      │
│  Communicates via REST API only (src/api/client.js)                  │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │ HTTP/JSON
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (FastAPI)                      │
│                                                                     │
│  ┌──────────┐  ┌───────────┐  ┌────────────┐  ┌────────┐            │
│  │ Auth     │  │ Students  │  │ Attendance │  │ Risk   │            │
│  │ Service  │  │ Service   │  │ Service    │  │ Service│            │
│  └──────────┘  └───────────┘  └─────┬──────┘  └───┬────┘            │
│                                     │             │                 │
└─────────────────────────────────────┼─────────────┼───────────────┘
                                      │             │
                    ┌─────────────────┼─────────────┼──────────┐
                    │                 ▼             ▼          │
                    │  ┌──────────────────┐  ┌──────────────┐  │
                    │  │ VISION MODULE    │  │ ML MODULE    │  │
                    │  │ vista/vision/    │  │ vista/ml/    │  │
                    │  │                  │  │              │  │
                    │  │ recognize()      │  │ calculate_   │  │
                    │  │ → detection      │  │ risk()       │  │
                    │  │ → embedding      │  │ → features   │  │
                    │  │ → matching       │  │ → scoring    │  │
                    │  │ → liveness       │  │ → overrides  │  │
                    │  └──────────────────┘  └──────────────┘  │
                    │           INTELLIGENCE LAYER             │
                    └──────────────────────────────────────────┘
                                       │
                                       ▼
                    ┌───────────────────────────────────────────┐
                    │           DATA LAYER                      │
                    │  SQLite (dev) / PostgreSQL (prod)         │
                    │  Tables: classrooms, students, attendance,│
                    │          scores, risk_flags, users        │
                    └───────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Vision Module (`vista/vision/`)

| File | Responsibility | Input | Output |
|---|---|---|---|
| `detect.py` | Face detection | Image path | List of face bounding boxes + landmarks |
| `embed.py` | Embedding extraction | Aligned face crop | 512-dim float vector |
| `match.py` | Identity matching | Embedding + stored embeddings | Best match student_id + similarity |
| `liveness.py` | Anti-spoofing | Face crop | Boolean (real/fake) |
| `recognize.py` | Pipeline orchestrator | Image path | `{student_id, confidence, liveness_passed}` |
| `enroll.py` | Face registration | Image(s) + student_id | Stored embedding in DB |

### 2.2 Backend Module (`vista/backend/app/`)

| File | Responsibility |
|---|---|
| `main.py` | FastAPI app, CORS, router registration, startup seed |
| `db.py` | SQLAlchemy engine, session, table creation, seed data, `get_student_metrics()` |
| `routes/auth.py` | Login/logout, JWT creation, token validation, role guards |
| `routes/students.py` | Student list/detail endpoints |
| `routes/attendance.py` | Mark attendance (vision integration), log, override |
| `routes/risk.py` | Risk flag endpoints, recompute trigger |
| `routes/export.py` | CSV export |
| `models/student.py` | Classroom + Student ORM models |
| `models/attendance.py` | Attendance + Score + RiskFlag ORM models |
| `models/user.py` | User ORM model |

### 2.3 ML Module (`vista/ml/`)

| File | Responsibility |
|---|---|
| `features.py` | Compute 8 engineered features from raw metrics |
| `risk_engine.py` | Rule-based scoring + XGBoost inference + reason generation |
| `train.py` | Model training pipeline (XGBoost + LR comparison) |
| `model.pkl` | Serialized trained model artifact |
| `data/generate_sample_data.py` | Synthetic dataset generator |
| `data/student_data.csv` | 200-row training dataset |
| `validate_uci.py` | External dataset validation |
| `test_risk_engine.py` | 7 integration test cases |

### 2.4 Frontend Module (`vista/frontend/src/`)

| File | Responsibility |
|---|---|
| `api/client.js` | Centralized API layer — all backend calls |
| `pages/Login.jsx` | Authentication form |
| `pages/Dashboard.jsx` | Overview: stats + at-risk students |
| `pages/AttendanceLog.jsx` | Date-filtered log + override + export |
| `pages/RiskFlags.jsx` | Risk cards + filter + recompute |
| `components/Layout.jsx` | Sidebar navigation + user info |
| `App.jsx` | Routing + auth state management |

---

## 3. Module Boundaries (Strict)

```
vision/ ──── DOES NOT import from backend/ or ml/
ml/     ──── DOES NOT import from vision/ or frontend/
backend/ ─── IMPORTS vision.recognize() and ml.calculate_risk_from_metrics()
frontend/ ── COMMUNICATES only via HTTP API (never imports Python)
```

### Fixed Entry Points (signatures never change)

```python
# vision/recognize.py
def recognize(image_path: str) -> dict:
    # Returns: {student_id: str|None, confidence: float, liveness_passed: bool}

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
| Authentication | JWT (HS256), 8-hour expiry |
| Password storage | bcrypt, cost factor ≥ 12 |
| Authorization | Role-based (admin/teacher) via `require_admin` dependency |
| Token revocation | In-memory blocklist (pilot; Redis in Phase 2) |
| CORS | Whitelist localhost:3000 and localhost:5173 |
| Input validation | Pydantic models on all request bodies |
| File handling | Temp files deleted immediately after vision processing |

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
