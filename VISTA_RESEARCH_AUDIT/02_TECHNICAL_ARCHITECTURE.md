# Document 2 — Technical Architecture

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 5 (Technical Architecture)
**Basis:** `audit-inspection.md` (Phase 2-3), direct source code inspection of `vista/vision/`, `vista/backend/`, `vista/frontend/`, `vista/ml/`.

---

## 1. Complete Architecture Overview

VISTA is a layered, client-server architecture with four operational tiers: Presentation (React frontend), Vision Intelligence (face recognition pipeline), Application Services (FastAPI backend), and Relational Persistence (SQLite/SQLAlchemy). [VERIFIED — `paper/figures/architecture.mmd`, `vista/md-docs/ARCHITECTURE.md`, `audit-inspection.md`]

### Frontend

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Framework | React 18 + Vite | [VERIFIED — `vista/frontend/package.json`] |
| Structure | Single-page application, single 88 KB monolithic `App.jsx` | [VERIFIED — `vista/frontend/src/App.jsx`] |
| Styling | Tailwind CSS (per paper) | [DOCUMENTED ONLY — stated in `PAPER.md` III-A] |
| API Client | `src/api/client.js` | [VERIFIED — file exists] |
| Build | Vite → `dist/` served via nginx | [VERIFIED — `vista/frontend/Dockerfile`, `nginx.conf`, `vite.config.js`] |
| Role portals | Admin Control Centre, Teacher Console, Student Self-Service Portal | [VERIFIED — `audit-inspection.md` confirms 3-role portals] |
| Real-time | WebSocket connection to `/ws/dashboard` | [VERIFIED — `vista/backend/app/websocket.py`] |
| Status | **Implemented** | |

### Backend

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Framework | FastAPI (Python 3.11) | [VERIFIED — `vista/backend/app/main.py`, `vista/backend/requirements.txt`] |
| Routes | 120 registered API routes | [VERIFIED — `audit-inspection.md`, `CLAIMS_TABLE.md` C-28] |
| Route modules | 14 route files (`auth`, `students`, `attendance`, `risk`, `export`, `enroll`, `lms`, `admin`, `coach`, `dashboards`, `student_portal`, `notifications`, `reports`, `academics`) | [VERIFIED — `vista/backend/app/routes/` directory listing] |
| ORM | SQLAlchemy | [VERIFIED — `vista/backend/app/models/`] |
| Server | Uvicorn (dev) / Gunicorn (prod) | [VERIFIED — `vista/gunicorn.conf.py`] |
| WebSocket | `/ws/dashboard` with JWT auth | [VERIFIED — `vista/backend/app/websocket.py`] |
| Scheduler | APScheduler (nightly risk recompute at 02:00 UTC) | [VERIFIED — `vista/backend/app/scheduler.py:recompute_all_risk_job`] |
| Status | **Implemented** | |

### Database

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Engine | SQLite (dev) via SQLAlchemy ORM | [VERIFIED — `vista/backend/app/db.py`, default `sqlite:///./vista_dev.db`] |
| Tables | 27 | [VERIFIED — `vista/docs/DB_SCHEMA.md`, confirmed programmatically in `audit-inspection.md`] |
| Config | `VISTA_DB_URL` env var | [VERIFIED — `.env.example`] |
| Multiple copies | root (6.7 MB), `vista/` (856 KB), `vista/backend/` (6.8 MB) | [VERIFIED — inventory; backend copy is canonical] |
| Status | **Implemented** (SQLite only; PostgreSQL mentioned in `vista/requirements.txt` via `psycopg2-binary` but not deployed) | [PARTIALLY VERIFIED] |

### ML Components

| Component | Technology | Location | Status |
|-----------|-----------|----------|--------|
| Face detection | SCRFD (`det_10g.onnx`) via InsightFace `buffalo_l` | `vista/vision/detect.py` | [VERIFIED — Implemented] |
| Face embedding | ArcFace R50 (`w600k_r50.onnx`) 512-dim L2-normalized | `vista/vision/embed.py` (utilities), `detect.py` (extraction) | [VERIFIED — Implemented] |
| Cosine matching | `np.dot()` on L2-normalized vectors, threshold 0.55 | `vista/vision/match.py` | [VERIFIED — Implemented] |
| ResNet-50 fallback | ImageNet-pretrained ResNet-50, custom head, `best_model_npz_splitB.pth` | `vista/vision/personal_classifier.py` | [VERIFIED — Implemented] |
| Cascade orchestrator | detect → cosine → ResNet-50 fallback → liveness | `vista/vision/recognize.py` | [VERIFIED — Implemented] |
| Liveness detection | Heuristic: det_score, face width, Laplacian variance | `vista/vision/liveness.py` | [VERIFIED — Implemented, but NOT neural anti-spoofing] |
| Multi-face tracker | ByteTrack-inspired IoU tracker | `vista/vision/tracker.py` | [PARTIALLY VERIFIED — implemented but NOT wired to attendance routes, `audit-inspection.md` D-5] |
| Risk engine (production) | Deterministic rule-based, 8 features, weighted score | `vista/ml/risk_engine.py` | [VERIFIED — Implemented] |
| Risk model (auxiliary) | XGBoost 3-class, 5 features, SHAP explainability | `vista/ml/model.pkl`, `vista/ml/explainer.py` | [VERIFIED — Implemented, below baseline performance] |
| CIE policy engine | VTU 3-test rules, best-2-of-3 | `vista/backend/app/cie_policy.py` | [VERIFIED — Implemented] |
| AI study coach | OpenRouter/Ollama LLM with deterministic fallback | `vista/backend/app/services/coach_service.py` | [VERIFIED — Implemented] |

### Authentication

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Mechanism | JWT (HS256), 8-hour expiry | [VERIFIED — `vista/backend/app/routes/auth.py`] |
| Password hashing | bcrypt, 12 rounds | [VERIFIED — `auth.py`] |
| Token blocklist | In-memory `set[str]` (not persistent across restarts) | [PARTIALLY VERIFIED — pilot-grade only, `audit-inspection.md`] |
| Rate limiting | 5 login attempts / 5 min / IP, in-memory | [PARTIALLY VERIFIED — not persistent] |
| Roles | 3 active: admin, teacher, student; 3 legacy rejected: hos, hop, mentor | [VERIFIED — `auth.py` enforces 403 ROLE_DEPRECATED] |
| Secret | `VISTA_JWT_SECRET` env var, insecure fallback default | [PARTIALLY VERIFIED — warning logged on startup] |
| Status | **Implemented** (with pilot-grade caveats) | |

### External Integrations

| Integration | Purpose | Evidence | Status |
|-------------|---------|---------|--------|
| InsightFace (ONNX models) | SCRFD + ArcFace face recognition | `vista/vision/detect.py` | [VERIFIED — downloads `det_10g.onnx`, `w600k_r50.onnx` at first use] |
| OpenRouter API | Cloud LLM for study coach | `coach_service.py:_call_openrouter()` | [VERIFIED — configurable via `LLM_USE_API`, `OPENROUTER_API_KEY`] |
| Ollama | Local LLM for study coach | `coach_service.py:_call_ollama()` | [VERIFIED — configurable via `LLM_USE_OLLAMA`, `OLLAMA_BASE_URL`] |
| APScheduler | Nightly risk recompute cron job | `vista/backend/app/scheduler.py` | [VERIFIED — requires `VISTA_SCHEDULER_ENABLED=true`] |

---

## 2. Data Flow Between Modules

### Attendance Marking Flow (Primary Path)

```
Teacher uploads classroom photo (React frontend)
  → POST /api/v1/attendance/mark or /mark-batch (FastAPI)
    → recognize() / recognize_all() (vista/vision/recognize.py)
      → Step 1: FaceDetector.detect_single() / detect() [SCRFD, detect.py]
      → Step 2: check_liveness() [liveness.py — heuristic]
      → Step 3: _classify_detected_face()
        → _match_student_gallery() [cosine match, match.py, τ=0.55]
          → if matched: return student_id + confidence
          → if not matched: classify_face() [ResNet-50, personal_classifier.py, τ=0.60]
            → if softmax ≥ 0.60: return student_id + confidence
            → else: return Unknown
    → Attendance record written to SQLite (source='face')
    → Audit log entry (user, IP, timestamp, student USN)
    → WebSocket push to dashboard
  → Response to frontend (student_id, confidence, liveness_passed)
```

[VERIFIED — `vista/vision/recognize.py` implements this exact flow; `vista/backend/app/routes/attendance.py` calls `recognize()`/`recognize_all()`]

### Risk Scoring Flow

```
Nightly APScheduler job (02:00 UTC) OR manual /risk/recompute-all
  → calculate_risk_from_metrics() [risk_engine.py — deterministic]
    → FeatureVector from StudentMetrics [features.py — 8 features]
    → Weighted risk score (attendance 0.30, marks 0.25, drop 0.15,
       decline 0.15, consecutive 0.10, engagement 0.05)
    → Override rules (consecutive ≥7 → HIGH, attendance <50% → HIGH, etc.)
    → RiskFlag persisted to risk_flags table
  → (Separate, on-demand) /risk/explain endpoint
    → run_pipeline_with_shap() [risk_engine.py — XGBoost + SHAP]
    → explainer.explain_prediction() [explainer.py — TreeExplainer]
    → Returns per-feature Shapley attributions (diagnostic only)
```

[VERIFIED — `vista/ml/risk_engine.py` has both paths; `vista/backend/app/routes/risk.py` confirms production uses rule engine, SHAP is diagnostic only]

### AI Coach Flow

```
Student sends message (React frontend)
  → POST /api/v1/coach/chat (FastAPI)
    → chat_with_coach() [coach_service.py]
      → Save user message to chat_messages table
      → get_coach_facts(student_id, db) — deterministic fact extraction
      → Check provider flags (LLM_USE_API, LLM_USE_OLLAMA)
        → If OpenRouter configured: _call_openrouter()
          → System prompt with facts dict (NO PII) + user query in XML tags
          → LLM generates response (temp=0.2, max_tokens=500)
        → If Ollama configured: _call_ollama() (100% on-premise)
        → Else: generate_rule_based_reply() (deterministic fallback)
      → Save assistant reply to chat_messages table
    → Return {reply, provider, model, facts_used}
```

[VERIFIED — `coach_service.py` implements this exact flow; PII sanitization confirmed in `_call_openrouter()` — only `facts` dict (numerical aggregates) is sent, labeled "NO PII"]

---

## 3. Deployment Architecture

### Current (Development/Pilot)

```
┌─────────────────────────────────────────────────────────┐
│  Single Host Machine (Intel i7-13700H, Windows 11)       │
│                                                          │
│  ┌─────────────┐    ┌──────────────────────────────────┐ │
│  │  React SPA   │    │  FastAPI Backend (Uvicorn)       │ │
│  │  (Vite dev   │───▶│  Port 8002 (live) / 8003         │ │
│  │  server or   │    │                                  │ │
│  │  nginx dist) │◀───│  120 REST endpoints              │ │
│  └─────────────┘    │  WebSocket /ws/dashboard          │ │
│                      │                                  │ │
│                      │  ┌─────────────────────────────┐  │ │
│                      │  │  Vision Pipeline (CPU)      │  │ │
│                      │  │  SCRFD + ArcFace (ONNX)     │  │ │
│                      │  │  ResNet-50 (PyTorch CPU)    │  │ │
│                      │  └─────────────────────────────┘  │ │
│                      │                                  │ │
│                      │  ┌─────────────────────────────┐  │ │
│                      │  │  ML Risk Engine              │  │ │
│                      │  │  Rule-based (production)     │  │ │
│                      │  │  XGBoost + SHAP (diagnostic) │  │ │
│                      │  └─────────────────────────────┘  │ │
│                      │                                  │ │
│                      │  ┌─────────────────────────────┐  │ │
│                      │  │  AI Coach Service            │  │ │
│                      │  │  OpenRouter (cloud) /        │  │ │
│                      │  │  Ollama (local) /            │  │ │
│                      │  │  Rule-based fallback         │  │ │
│                      │  └─────────────────────────────┘  │ │
│                      └───────────┬──────────────────────┘ │
│                                  │                         │
│                      ┌───────────▼──────────────────────┐  │
│                      │  SQLite (vista_dev.db)           │  │
│                      │  27 tables                       │  │
│                      └──────────────────────────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  File Storage                                       │ │
│  │  dataset/ (raw face images, 1.94 GB)               │ │
│  │  agumented data/ (augmented, 225 MB)                │ │
│  │  data/processed/ (NPZ embeddings, 1.15 GB)          │ │
│  │  training_results/ (ResNet-50 checkpoints)           │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         │ (only if LLM_USE_API=true)
         ▼
┌─────────────────────┐
│  OpenRouter (cloud)  │
│  LLM API endpoint    │
│  (no PII sent)        │
└─────────────────────┘
```

[VERIFIED — deployment is single-host, CPU-only, SQLite; `audit-inspection.md` confirms CPU-only inference, SQLite default DB; coach_service.py confirms external LLM only for coaching]

### Docker (Defined but Not Production-Tested)

| File | Purpose | Status |
|------|---------|--------|
| `vista/docker-compose.yml` | Backend + frontend composition | [PARTIALLY VERIFIED — file present, not production-tested per `audit-inspection.md`] |
| `vista/Dockerfile` | Backend image | [DOCUMENTED ONLY] |
| `vista/frontend/Dockerfile` | Frontend nginx image | [DOCUMENTED ONLY] |
| `vista/gunicorn.conf.py` | Production server config | [DOCUMENTED ONLY] |

---

## 4. Implementation Status Per Component

| Component | Status | Evidence |
|-----------|--------|---------|
| SCRFD Face Detection | ✅ Implemented | `detect.py` |
| ArcFace R50 Embedding | ✅ Implemented | `detect.py` (InsightFace combined), `embed.py` |
| ArcFace Cosine Matching | ✅ Implemented | `match.py`, τ=0.55 |
| ResNet-50 Cascade Fallback | ✅ Implemented | `personal_classifier.py`, `recognize.py` |
| Two-Stage Cascade Pipeline | ✅ Implemented | `recognize.py` |
| Face Enrollment | ✅ Implemented | `enroll.py` |
| Multi-Face Batch Attendance | ✅ Implemented | `recognize_all()`, `mark-batch` endpoint |
| Heuristic Liveness Detection | ✅ Implemented | `liveness.py` |
| Neural Anti-Spoofing (MiniFASNet) | ❌ Not Implemented | Future roadmap only |
| ByteTrack Multi-Frame Tracker | ⚠️ Partial (not wired) | `tracker.py` exists, not connected to routes |
| Deterministic Rule-Based Risk | ✅ Implemented | `risk_engine.py` |
| Feature Engineering | ✅ Implemented | `features.py` |
| XGBoost Risk Model (Auxiliary) | ✅ Implemented (below baseline) | `model.pkl`, `train.py` |
| SHAP Explainability | ✅ Implemented | `explainer.py` |
| CIE Policy Engine | ✅ Implemented | `cie_policy.py` |
| AI Study Coach (Deterministic) | ✅ Implemented | `coach_service.py` |
| AI Study Coach (LLM via OpenRouter) | ✅ Implemented | `coach_service.py` |
| AI Study Coach (Ollama) | ✅ Implemented | `coach_service.py` |
| FastAPI Backend (120 routes) | ✅ Implemented | `main.py` |
| JWT Authentication (3-role RBAC) | ✅ Implemented (pilot-grade) | `auth.py` |
| 27-Table SQLite Schema | ✅ Implemented | Verified programmatically |
| Audit Logging / Provenance | ✅ Implemented | `audit.py`, `source` column |
| Real-Time WebSocket Updates | ✅ Implemented | `websocket.py` |
| In-App Notifications | ✅ Implemented | `notifications.py` |
| React Frontend (3-role portals) | ✅ Implemented | `App.jsx` |
| Nightly Risk Recompute | ✅ Implemented | `scheduler.py` |
| Parent Alert System | ⚠️ Partial | Table exists, delivery mechanism unclear |
| Cross-Validation for Risk Model | ❌ Not Implemented | Single split only |
| Open-Set Face Evaluation | ❌ Not Implemented | Closed-set only |
| GPU Inference Acceleration | ❌ Not Implemented | CPU-only |
| Multi-Institution/Multi-Classroom | ❌ Not Implemented | Pilot: 1 classroom |
| Docker Production Deployment | ⚠️ Partial | Files present, not tested |
| Persistent Token Blocklist | ❌ Not Implemented | In-memory only |
| Data Encryption at Rest | ❌ Not Implemented | SQLite plaintext |

---

## 5. Text-Based Architecture Diagram (ASCII)

```
╔══════════════════════════════════════════════════════════════════╗
║                        VISTA SYSTEM ARCHITECTURE                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌─────────────────────── PRESENTATION TIER ─────────────────────┐ ║
║  │                                                              │ ║
║  │  ┌─────────────────────────────────────────────────────────┐ │ ║
║  │  │  React 18 SPA (App.jsx, 88 KB monolith)                 │ │ ║
║  │  │  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐ │ │ ║
║  │  │  │  Admin    │  │ Teacher  │  │ Student Self-Service   │ │ │ ║
║  │  │  │  Control  │  │ Console  │  │ Portal (read-only)     │ │ │ ║
║  │  │  │  Centre   │  │ (camera  │  │ (attendance, CIE,      │ │ │ ║
║  │  │  │          │  │  upload) │  │  risk, coach chat)      │ │ │ ║
║  │  │  └──────────┘  └──────────┘  └────────────────────────┘ │ │ ║
║  │  │         api/client.js (axios) → REST + WebSocket        │ │ ║
║  │  └─────────────────────────────────────────────────────────┘ │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                │                                   ║
║                    HTTPS / JWT Bearer Token                        ║
║                                │                                   ║
║  ┌─────────────────────── APPLICATION TIER ──────────────────────┐ ║
║  │                                                              │ ║
║  │  ┌─────────────────────────────────────────────────────────┐ │ ║
║  │  │  FastAPI Backend (Python 3.11, 120 routes, 14 modules)   │ │ ║
║  │  │                                                         │ │ ║
║  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │ │ ║
║  │  │  │  Auth     │ │Attendance│ │  Risk    │ │  Coach     │  │ │ ║
║  │  │  │  (JWT,    │ │ (mark,   │ │ (rule +  │ │ (LLM +     │  │ │ ║
║  │  │  │   RBAC)  │ │  batch)  │ │  SHAP)   │ │  fallback) │  │ │ ║
║  │  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │ │ ║
║  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │ │ ║
║  │  │  │  Enroll  │ │  Export  │ │  LMS     │ │ Dashboard  │  │ │ ║
║  │  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │ │ ║
║  │  │                                                         │ │ ║
║  │  │  ┌──────────────────┐  ┌─────────────────────────────┐  │ │ ║
║  │  │  │  CIE Policy      │  │  Scheduler (APScheduler)    │  │ │ ║
║  │  │  │  Engine          │  │  Nightly risk recompute      │  │ │ ║
║  │  │  │  (cie_policy.py)  │  │  02:00 UTC                  │  │ │ ║
║  │  │  └──────────────────┘  └─────────────────────────────┘  │ │ ║
║  │  └─────────────────────────────────────────────────────────┘ │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                │                                   ║
║  ┌─────────────────────── VISION TIER ──────────────────────────┐ ║
║  │                                                              │ ║
║  │  ┌─────────────────────────────────────────────────────────┐ │ ║
║  │  │  recognize() / recognize_all() — Cascade Orchestrator   │ │ ║
║  │  │                                                         │ │ ║
║  │  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │ │ ║
║  │  │  │  SCRFD      │───▶│  Liveness   │───▶│  ArcFace    │  │ │ ║
║  │  │  │  Detection  │    │  (heuristic)│    │  Cosine     │  │ │ ║
║  │  │  │  (ONNX CPU) │    │  det_score  │    │  Match      │  │ │ ║
║  │  │  │  det_10g    │    │  + width    │    │  τ=0.55     │  │ │ ║
║  │  │  └─────────────┘    │  + Laplacian│    └──────┬──────┘  │ │ ║
║  │  │                     └─────────────┘           │         │ │ ║
║  │  │                                               │ match?  │ │ ║
║  │  │                                      ┌────────▼──────┐  │ │ ║
║  │  │                                      │  YES → return │  │ │ ║
║  │  │                                      └────────┬──────┘  │ │ ║
║  │  │                                               │ NO      │ │ ║
║  │  │                                      ┌────────▼──────┐  │ │ ║
║  │  │                                      │  ResNet-50     │  │ │ ║
║  │  │                                      │  Fallback     │  │ │ ║
║  │  │                                      │  τ=0.60       │  │ │ ║
║  │  │                                      │  (PyTorch CPU)│  │ │ ║
║  │  │                                      └───────────────┘  │ │ ║
║  │  └─────────────────────────────────────────────────────────┘ │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                │                                   ║
║  ┌─────────────────────── PERSISTENCE TIER ─────────────────────┐ ║
║  │                                                              │ ║
║  │  ┌─────────────────────────────────────────────────────────┐ │ ║
║  │  │  SQLite (SQLAlchemy ORM) — 27 tables                     │ │ ║
║  │  │  users | students(+embedding) | attendance(+source) |     │ │ ║
║  │  │  scores | risk_flags | audit_logs | chat_messages |      │ │ ║
║  │  │  notifications | interventions | subjects | ...           │ │ ║
║  │  └─────────────────────────────────────────────────────────┘ │ ║
║  │                                                              │ ║
║  │  ┌─────────────────────────────────────────────────────────┐ │ ║
║  │  │  File Storage (local)                                    │ │ ║
║  │  │  dataset/ → raw images → facial_pipeline.py → NPZ       │ │ ║
║  │  │  training_results/ → best_model_npz_splitB.pth           │ │ ║
║  │  └─────────────────────────────────────────────────────────┘ │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  ┌─────────────────────── EXTERNAL (optional) ──────────────────┐ ║
║  │  ┌─────────────────────┐         ┌─────────────────────┐    │ ║
║  │  │  OpenRouter (cloud) │         │  Ollama (local)       │    │ ║
║  │  │  LLM for coach       │         │  LLM for coach        │    │ ║
║  │  │  (NO PII sent)       │         │  (100% on-premise)    │    │ ║
║  │  └─────────────────────┘         └─────────────────────┘    │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 6. Tech Stack Table

| Component | Technology | Version (if known) | Status |
|-----------|-----------|-------------------|--------|
| Frontend framework | React | 18 | [VERIFIED] Implemented |
| Frontend build | Vite | — | [VERIFIED] Implemented |
| CSS framework | Tailwind CSS | — | [DOCUMENTED ONLY] |
| Backend framework | FastAPI | 0.111.0 (per paper) | [VERIFIED] Implemented |
| Backend language | Python | 3.11.9 | [VERIFIED] Implemented |
| ORM | SQLAlchemy | — | [VERIFIED] Implemented |
| Database | SQLite | — | [VERIFIED] Implemented (dev only) |
| Database (target) | PostgreSQL | — | [DOCUMENTED ONLY] `psycopg2-binary` in requirements, not deployed |
| Auth | JWT (HS256) + bcrypt | 12 rounds | [VERIFIED] Implemented |
| Face detection | SCRFD (InsightFace buffalo_l) | `det_10g.onnx` | [VERIFIED] Implemented |
| Face embedding | ArcFace R50 | `w600k_r50.onnx` | [VERIFIED] Implemented |
| Face matching | NumPy cosine similarity | — | [VERIFIED] Implemented |
| Cascade fallback | ResNet-50 (PyTorch) | 2.3.1 (per paper) | [VERIFIED] Implemented |
| Liveness | Heuristic (OpenCV) | 4.10.0 (per paper) | [VERIFIED] Implemented, non-neural |
| ONNX runtime | ONNX Runtime | 1.18.0 (per paper) | [VERIFIED] CPUExecutionProvider |
| Risk model | XGBoost | 2.0.3 (per paper) / 3.2.0 (live env) | [VERIFIED] Implemented |
| Explainability | SHAP | 0.45.1 (per paper) / 0.51.0 (live env) | [VERIFIED] Implemented |
| ML framework | scikit-learn | 1.9.1 (live env) | [VERIFIED] |
| Scheduler | APScheduler | — | [VERIFIED] Implemented |
| WebSocket | FastAPI WebSocket | — | [VERIFIED] Implemented |
| LLM (cloud) | OpenRouter | configurable model | [VERIFIED] Implemented |
| LLM (local) | Ollama | configurable model | [VERIFIED] Implemented |
| Deployment | Docker + Gunicorn | — | [PARTIALLY VERIFIED] Defined, not tested |
| Web server (prod) | nginx | — | [DOCUMENTED ONLY] Defined for frontend container |

---

## 7. Module-Level Explanation of Each Subsystem

### Vision Subsystem (`vista/vision/`)

The vision pipeline is the most complex subsystem, implementing a two-stage cascade face recognition architecture. The flow is: SCRFD detection → heuristic liveness check → ArcFace cosine matching (τ=0.55) → ResNet-50 fallback (τ=0.60) → result. The ResNet-50 classifier is fine-tuned on a 20-student dataset with 30 augmentation variants per source image, using ImageNet-pretrained weights (not ArcFace weights). The classifier head has two BatchNorm and two Dropout layers for regularization. [VERIFIED — `recognize.py`, `personal_classifier.py`, `detect.py`, `match.py`, `liveness.py`, `enroll.py` all inspected directly]

The liveness module is explicitly heuristic (detection confidence, face width, Laplacian variance), not neural. The paper's formula references EAR (Eye Aspect Ratio), but the code does NOT implement EAR — this is a documentation discrepancy. [CONTRADICTED — `liveness.py` has no EAR computation; `PAPER.md` Section IV-A formula uses EAR. `audit-inspection.md` D-3]

A multi-face tracker (`tracker.py`) is implemented but not wired to attendance routes, which use single-frame recognition instead. [PARTIALLY VERIFIED — `audit-inspection.md` D-5]

### ML Risk Subsystem (`vista/ml/`)

The risk subsystem has two parallel paths. The production path is a deterministic rule engine (`calculate_risk_from_metrics`) that computes a weighted risk score from 8 features with override rules. The auxiliary path is an XGBoost 3-class model with SHAP explainability, used only by the `/risk/explain` diagnostic endpoint. The XGBoost model achieves 50% accuracy (below the 53.5% majority baseline), which is honestly disclosed. The training data is synthetic (`student_data.csv`, 1000 rows) with labels generated by deterministic rules mirroring the rule engine, creating a circular training signal. [VERIFIED — `risk_engine.py`, `features.py`, `explainer.py`, `train.py`, `risk_model_evaluation.json`]

### Backend Application (`vista/backend/`)

The backend is a FastAPI application with 120 routes across 14 modules. It implements JWT-based 3-role RBAC, audit logging with provenance tags (`source='face'|'manual'|'seed'`), a CIE policy engine for VTU academic rules, an AI study coach with deterministic computation firewall, and APScheduler for nightly risk recomputation. [VERIFIED — `main.py`, `routes/`, `auth.py`, `audit.py`, `cie_policy.py`, `coach_service.py`, `scheduler.py`]

### Frontend (`vista/frontend/`)

The frontend is a React 18 SPA built with Vite, structured as a single 88 KB monolithic `App.jsx` file with three role-scoped portals. It communicates with the backend via a REST API client and WebSocket for real-time dashboard updates. [VERIFIED — `App.jsx`, `api/client.js`, `vite.config.js`]

---

*End of Document 2 — Technical Architecture*
