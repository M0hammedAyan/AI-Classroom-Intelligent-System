# VISTA — Universal Project Intelligence File

> **This file is the single source of truth.** Read it before touching ANY file in this repo.
> It contains: project vision, architecture, research mapping, implementation status,
> roadmap, risks, and decisions. Updated every time a feature is added or completed.
>
> **Last updated:** 2026-06-24 — Full architecture review + roadmap created.

---

## 1. What VISTA Is

**VISTA (Visual Intelligence System for Tracking and Analysis)** is an AI-powered academic
intelligence platform that combines:

1. **Automated Attendance** — camera → face detection → recognition → attendance record
2. **Academic Risk Prediction** — attendance + scores → feature engineering → ML classification
3. **Explainable AI** — reasons, confidence, recommendations per prediction
4. **Educator Dashboard** — role-gated UI showing logs, flags, exports

### Problem Statement

Current attendance systems are manual, error-prone, and stop at recording presence.
They do not analyze performance, predict risk, or recommend interventions.
VISTA solves this by answering:
- Which students are at risk?
- Why are they at risk?
- What factors contribute?
- What interventions are recommended?
- How is performance changing over time?

### Expected Users

| Role | Access |
|---|---|
| Teacher | View attendance, risk flags, override records, export reports |
| Admin | All teacher access + recompute risk, manage users |
| (Phase 2) Mentor, HOD, Student | Not built in pilot |

---

## 2. Pilot Scope — Hard Constraints

This is a **3-month MVP** built by 4 students (~2–3 hrs/day).

| Constraint | Value |
|---|---|
| Classrooms | 1 |
| Students | 20–30 |
| Risk engine | Rule-based + XGBoost (synthetic data) |
| Infrastructure | Dev laptop — no GPU, no cloud |
| Dashboard | Single role-gated view (admin/teacher) |
| Auth | JWT, 8-hour expiry — no refresh endpoint |
| Vision | Single-image recognition (not video stream in pilot) |

**If a task requires going beyond any of the above, stop and flag it.**

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VISTA SYSTEM ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────────────┘

  Classroom Camera / Image Upload
         │
         ▼
┌─────────────────────────┐       ┌──────────────────────────────────────┐
│   VISION MODULE         │       │   BACKEND (FastAPI)                   │
│   vista/vision/         │       │   vista/backend/app/                  │
│                         │       │                                      │
│  detect.py (SCRFD)      │       │  routes/auth.py        ✅            │
│  embed.py (ArcFace R50) │       │  routes/students.py    ✅            │
│  match.py (cosine sim)  │       │  routes/attendance.py  ✅            │
│  liveness.py (MiniFAS)  │       │  routes/risk.py        ✅            │
│  recognize.py (pipeline)│──────▶│  routes/export.py      ✅            │
│                         │       │  db.py + models/       ✅            │
└─────────────────────────┘       └──────────────┬───────────────────────┘
                                                 │
                              ┌──────────────────┼──────────────────┐
                              ▼                                     ▼
               ┌──────────────────────────┐          ┌─────────────────────────┐
               │   ML MODULE              │          │   FRONTEND (React+Vite) │
               │   vista/ml/              │          │   vista/frontend/        │
               │                          │          │                         │
               │  features.py        ✅   │          │  Login.jsx         ✅   │
               │  risk_engine.py     ✅   │          │  Dashboard.jsx     ✅   │
               │  train.py           ✅   │          │  AttendanceLog.jsx ✅   │
               │  model.pkl          ✅   │          │  RiskFlags.jsx     ✅   │
               │  __init__.py        ✅   │          │  api/client.js     ✅   │
               └──────────────────────────┘          └─────────────────────────┘
```

### Data Flow (End-to-End)

```
Teacher uploads image → POST /api/v1/attendance/mark
  → backend decodes image, saves temp file
  → vision.recognize(image_path)
    → detect.py: SCRFD → bounding boxes + landmarks
    → embed.py: ArcFace R50 → 512-dim vector
    → match.py: cosine similarity vs stored embeddings → best match
    → liveness.py: MiniFASNet → real/fake score
  → returns {student_id, confidence, liveness_passed}
  → backend writes attendance row to DB
  → response returned to frontend

Admin triggers recompute → POST /api/v1/students/{id}/risk/recompute
  → ml.calculate_risk_from_metrics(metrics)
    → features.py: compute 8 features from attendance + scores
    → risk_engine.py: weighted scoring + overrides
    → generate reasons + recommendations
  → backend writes risk_flag row to DB
  → response returned to frontend
```

---

## 4. Technology Decisions

### Vision Layer

| Component | Technology | Why |
|---|---|---|
| Face Detection | SCRFD (InsightFace built-in) | Faster than RetinaFace, same accuracy, pretrained on WIDER FACE |
| Face Embedding | ArcFace R50 (ResNet-50 backbone) | 512-dim; sufficient for 30 students; 15ms CPU inference; pretrained on MS1MV2 |
| Matching | Cosine similarity, threshold 0.55 | Simple, fast, no training needed at 30 students |
| Anti-spoofing | MiniFASNet (single-frame) | Works on JPEG; no video needed; pretrained |
| Tracking (Phase 2) | ByteTrack | IoU + Kalman; ideal for static classroom camera; no ReID network needed |

**Why NOT R100:** At 30 students in 512 dimensions, R50 and R100 produce identical discrimination. R50 is 2× faster.
**Why NOT DeepSORT:** Requires separate ReID network. ByteTrack uses detection confidence only — simpler + faster.
**Why NOT Deep OC-SORT:** Designed for non-linear motion (dance, sports). Students sit still. Overkill.

### ML Layer

| Component | Technology | Why |
|---|---|---|
| Rule-based scoring | Weighted formula + overrides | Works day 1 with zero training data |
| ML classifier | XGBoost (100 trees, depth 4) | Best on tabular data <10K rows; F1=0.957 on synthetic |
| Baseline | Logistic Regression | Interpretable; F1=0.94; good for comparison |
| Explainability | Template-based reasons (now); SHAP (Phase 2) | SHAP requires model; templates work with rules |
| Feature engineering | 8 handcrafted features | See FEATURE_ENGINEERING.md |

### Backend Layer

| Component | Technology | Why |
|---|---|---|
| Framework | FastAPI | Async, auto-docs, Pydantic validation |
| Database | SQLite (dev) / PostgreSQL (prod) | SQLAlchemy ORM; same models both |
| Auth | JWT (PyJWT) + bcrypt | 8-hour expiry; in-memory blocklist |
| Deps | fastapi, uvicorn, sqlalchemy, pyjwt, bcrypt | Minimal |

### Frontend Layer

| Component | Technology | Why |
|---|---|---|
| Framework | React 18 | Component-based; team knows it |
| Build | Vite 5 | Fast dev server; proxy to backend |
| Routing | react-router-dom 6 | SPA routing |
| Styling | Plain CSS (no framework) | Simple; no extra deps for pilot |
| API | Centralized client.js | One-line URL change to swap backend |

---

## 5. Research Paper Analysis & Literature Mapping

### Papers Referenced → VISTA Mapping

| Paper | Algorithm | VISTA Component | Status |
|---|---|---|---|
| ArcFace (Deng, CVPR 2019) | Angular margin loss, R100 embedding | `vision/embed.py` | ❌ Not implemented |
| RetinaFace / SCRFD (InsightFace) | Multi-task face detection | `vision/detect.py` | ❌ Not implemented |
| InsightFace toolkit | Unified detect + recognize | `vision/recognize.py` | ❌ Not implemented |
| ByteTrack (Zhang, ECCV 2022) | Two-stage IoU + Kalman tracking | Not in codebase | ❌ Phase 2 only |
| Deep OC-SORT (Maggiolino, 2023) | Observation-centric + ReID | Not in codebase | ❌ Phase 4 only |
| DeepSORT (Wojke, 2017) | Kalman + appearance ReID | Not in codebase | ❌ Superseded by ByteTrack |
| XGBoost (Chen & Guestrin, 2016) | Gradient boosted trees | `ml/train.py`, `ml/risk_engine.py` | ✅ Implemented |
| Logistic Regression | Linear classifier | `ml/train.py` | ✅ Implemented |
| SHAP (Lundberg & Lee, 2017) | Shapley value explanations | Not in codebase | ❌ Milestone 4 |
| FaceNet (Schroff, 2015) | Triplet loss embeddings | Not used (ArcFace preferred) | — |
| KappaFace | Adaptive margin | Not in codebase | ❌ Research only |
| Ramya et al. (2025) | AI attendance monitoring | Overall architecture | ⚠️ Partially aligned |

### Technology Selection Justification

| Choice | Alternatives Considered | Why This One |
|---|---|---|
| SCRFD (detection) | RetinaFace, MTCNN | Faster on CPU, same accuracy, built into InsightFace |
| ArcFace R50 (embedding) | R100, R18, FaceNet | R50 sufficient for 30 students; 2× faster than R100 |
| Cosine similarity | Euclidean, learned metric | Standard for normalized embeddings; no training needed |
| ByteTrack (Phase 2) | DeepSORT, Deep OC-SORT | Simplest; no ReID network; ideal for static camera |
| XGBoost (risk) | LightGBM, CatBoost, RF | Best tabular performance; SHAP-compatible; handles imbalance |
| Rule-based (pilot) | Pure ML | Works with zero training data; validates pipeline |
| MiniFASNet (liveness) | Depth camera, multi-frame | Single-frame; pretrained; no video needed |

---

## 6. Implementation Status

### Complete ✅

| Module | Component | Details |
|---|---|---|
| ML | `features.py` | 8 features per FEATURE_ENGINEERING.md |
| ML | `risk_engine.py` | Rule-based + XGBoost dual path, DB-wired |
| ML | `train.py` | XGBoost wins (F1=0.957), saved as model.pkl |
| ML | `test_risk_engine.py` | 7/7 tests pass |
| ML | `validate_uci.py` | UCI dataset sanity checker |
| ML | `__init__.py` | Public API exports |
| Backend | Auth routes | Login/logout, JWT, role guards |
| Backend | Student routes | List/detail |
| Backend | Attendance routes | Mark (vision stub), log (derived absent), override |
| Backend | Risk routes | Get, list, recompute |
| Backend | Export route | CSV (PDF not implemented) |
| Backend | DB + Models | All tables, seed data with realistic patterns |
| Backend | Mock server | Full contract-shaped fixture data |
| Frontend | Login page | Email/password, demo credentials shown |
| Frontend | Dashboard | Stats grid + at-risk students list |
| Frontend | Attendance Log | Date filter, status badges, override, CSV export |
| Frontend | Risk Flags | Cards, filter, admin recompute button |
| Frontend | Layout | Sidebar nav, user info, logout |
| Frontend | API client | Centralized, auth-aware |
| Docs | All 7 contract documents | Frozen, comprehensive |

### Not Built ❌ (Vision Module — Critical Path)

| File | What It Does | Blocks |
|---|---|---|
| `vision/detect.py` | SCRFD face detection | Everything in vision |
| `vision/embed.py` | ArcFace R50 embedding | Matching |
| `vision/match.py` | Cosine similarity matching | Recognition |
| `vision/liveness.py` | MiniFASNet anti-spoofing | Full pipeline |
| `vision/recognize.py` | Pipeline orchestrator | Backend integration |
| `vision/test_recognize.py` | Integration tests | Validation |
| `vision/enroll.py` or `enroll_cli.py` | Face registration | Having embeddings to match against |

---

## 7. Roadmap & Milestones

| # | Milestone | Status | Next Action |
|---|---|---|---|
| M0 | Planning & Documentation | ✅ Complete | — |
| M1 | Vision Pipeline | ❌ NEXT | Install InsightFace, implement detect→embed→match→recognize |
| M2 | Student Enrollment | ❌ Blocked on M1 | CLI/API to register faces |
| M3 | E2E Integration Test | ❌ Blocked on M2 | Full flow with real photos |
| M4 | SHAP Explainability | ❌ Independent | Add TreeExplainer to risk_engine |
| M5 | Multi-Face (Optional) | ❌ Low priority | Batch detection in single image |
| M6 | Production Hardening | ❌ Phase 2 | Docker, PostgreSQL, monitoring |

**See `md-docs/ROADMAP.md` for full details, effort estimates, and acceptance criteria.**

---

## 8. Key Decisions (Locked)

| # | Decision | Rationale |
|---|---|---|
| 1 | Liveness failure writes DB row with candidate student_id | Captures spoofing data cheaply |
| 2 | Unrecognized faces write no DB row | False-reject rate measured in test set |
| 3 | Risk recompute is manual, admin-only | No scheduled automation in pilot |
| 4 | JWT expiry 8 hours, no refresh | One login per school day sufficient |
| 5 | Absent derived at read time | No "close session" endpoint needed |
| 6 | ArcFace R50 (not R100) | Sufficient for 30 students, 2× faster |
| 7 | SCRFD (not MTCNN) | Faster, same accuracy, InsightFace built-in |
| 8 | ByteTrack deferred to Phase 2 | Requires video; pilot uses single image |
| 9 | Template reasons (not SHAP) for pilot | SHAP in Milestone 4 |
| 10 | SQLite for dev, PostgreSQL for prod | Same SQLAlchemy models |

---

## 9. Contract Documents

| File | What it is |
|---|---|
| `docs/API_CONTRACT.md` | Every endpoint, request/response schema, error codes |
| `docs/DB_SCHEMA.md` | Every table, column, FK, index |
| `docs/INTEGRATION_LOG.md` | Log of contract changes after Day 3 freeze |
| `docs/RISK_SYSTEM_DESIGN.md` | Risk indicators, scoring formula, override rules |
| `docs/FEATURE_ENGINEERING.md` | 8 features with formulas and examples |
| `docs/RISK_ENGINE_SPEC.md` | Full scoring logic, edge cases, 7 test cases |
| `docs/DATASET_ANALYSIS.md` | Public datasets evaluated for Phase 2 |
| `md-docs/PROJECT_PLAN.md` | Problem, goals, scope, requirements, constraints |
| `md-docs/ARCHITECTURE.md` | System architecture, component boundaries |
| `md-docs/DATABASE_DESIGN.md` | ER diagram, table specs, indexing |
| `md-docs/API_SPEC.md` | Endpoint summary, auth/error strategy |
| `md-docs/ML_DESIGN.md` | Features, models, training, explainability |
| `md-docs/ROADMAP.md` | Milestones, dependencies, testing, risks |

---

## 10. Rules That Apply to Every Module

1. **Read contract docs before writing code.**
2. **Build one feature at a time.** Implement → test → validate → proceed.
3. **Handle failure cases.** Not done until bad input is handled.
4. **Do not modify files outside your module** without logging in INTEGRATION_LOG.md.
5. **Log ambiguities** in your module's CLAUDE.md.
6. **Do not add undocumented dependencies.**
7. **Update this CLAUDE.md** after every milestone completion.

---

## 11. How to Run

### Backend
```bash
cd vista
python -m uvicorn vista.backend.app.main:app --host 127.0.0.1 --port 8000
```
Demo accounts: `admin@vista.local / admin123`, `teacher@vista.local / teacher123`

### Frontend
```bash
cd vista/frontend
npm install
npm run dev
```
Opens at http://localhost:5173 (proxies API to backend)

### ML Tests
```bash
python -m vista.ml.test_risk_engine
python -m vista.ml.train
```

### Frontend Build
```bash
cd vista/frontend
npm run build
```

---

## 12. Agent Response Convention

After completing any task anywhere in this repo, end response with:

**Built:** [1–2 sentences — what was implemented or changed]
**Next:** [1–2 specific actionable next steps]
**CLAUDE.md Updated:** [Yes/No — this file must be updated on every change]
