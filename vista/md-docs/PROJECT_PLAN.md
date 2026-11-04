# VISTA — Project Plan

> **Last Updated:** 2026-06-24
> **Status:** Complete — ready for implementation review.

---

## 1. Problem Statement

Current educational attendance systems are:
- Manual and error-prone
- Require human effort for every session
- Provide no analytical insights
- Stop at recording presence/absence

They do NOT:
- Analyze student performance trends
- Predict academic risk
- Provide actionable recommendations
- Generate explainable insights for educators

VISTA solves this by building an integrated platform that automates attendance
via face recognition AND identifies at-risk students with explainable predictions.

---

## 2. Project Goals

| # | Goal | Measurable Success Criteria |
|---|---|---|
| G-1 | Automate attendance via face recognition | ≥90% recognition accuracy on enrolled students |
| G-2 | Track multiple students per session | All enrolled students processed per image |
| G-3 | Maintain attendance history | Full semester history queryable by date/student |
| G-4 | Analyze attendance trends | Weekly/monthly trend features computed |
| G-5 | Predict academic risk | 3-class classification (LOW/MEDIUM/HIGH) |
| G-6 | Provide explainable outputs | Max 4 reasons + 3 recommendations per prediction |
| G-7 | Display insights via dashboard | Functional teacher/admin dashboard |
| G-8 | Export reports | CSV export of attendance data |

---

## 3. Scope Definition

### In Scope (Implemented)

- Multi-tier institution structure (Schools, Departments, Classes, Sections)
- Face detection (SCRFD) + recognition (ArcFace R50) + ResNet-50 personal classifier fallback
- Heuristic liveness verification (Laplacian variance, bounding box thresholds)
- Multi-face tracking via greedy IoU association (`tracker.py`)
- Attendance recording with confidence scores and manual teacher override
- Rule-based risk scoring + XGBoost inference + SHAP TreeExplainer (`explainer.py`)
- React dashboard supporting 3 active roles (Admin, Teacher, Student) with dark/light mode; legacy HOS/HOP/Mentor deprecated
- CSV and PDF export for attendance and academic performance reports
- Real-time updates via WebSocket (`/ws/dashboard`)
- Automated daily risk evaluation via APScheduler (`scheduler.py`)
- Student face enrollment (single & batch API in `enroll.py`)

### Out of Scope / Future Upgrades

- Real-time RTSP camera hardware integration
- Supervised ML trained on multi-semester real institutional outcome records (pilot uses synthetic data + UCI benchmark)
- Cloud Kubernetes orchestration (pilot uses Docker Compose / local server)

---

## 4. User Roles

| Role | Permissions | Status |
|---|---|---|
| Admin | All access + risk recompute + user/org management + audit logs | ✅ Implemented |
| HOS | School-wide monitoring, departments, staff, student analytics | ✅ Implemented |
| HOP | Department-level analytics, class assignments, teacher mapping | ✅ Implemented |
| Mentor | Assigned mentees watchlist, risk tracking, intervention logging | ✅ Implemented |
| Teacher | Class attendance (photo + manual), marks entry, assignments | ✅ Implemented |
| Student | Self-service portal: attendance breakdown, timetable, scores, study materials | ✅ Implemented |

---

## 5. Functional Requirements

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-01 | Detect faces in classroom image (SCRFD) | P0 | ✅ Implemented (`detect.py`) |
| FR-02 | Extract 512-dim face embeddings (ArcFace R50) | P0 | ✅ Implemented (`embed.py`) |
| FR-03 | Match embeddings via cosine similarity + ResNet classifier | P0 | ✅ Implemented (`match.py`, `personal_classifier.py`) |
| FR-04 | Anti-spoofing heuristic liveness check | P1 | ✅ Implemented (`liveness.py`) |
| FR-05 | `recognize(image_path)` entry point | P0 | ✅ Implemented (`recognize.py`) |
| FR-06 | Mark attendance via image upload API | P0 | ✅ Implemented (`attendance.py`, `facial_pipeline.py`) |
| FR-07 | Derive absent status at read time | P0 | ✅ Implemented |
| FR-08 | Manual attendance override | P1 | ✅ Implemented |
| FR-09 | Compute risk from attendance + scores | P0 | ✅ Implemented (`risk_engine.py`) |
| FR-10 | Explainable reasons + SHAP recommendations | P0 | ✅ Implemented (`explainer.py`, `risk_engine.py`) |
| FR-11 | Admin & scheduled daily risk recompute | P1 | ✅ Implemented (`risk.py`, `scheduler.py`) |
| FR-12 | Role-gated JWT authentication (3 active roles) | P0 | ✅ Implemented (`auth.py`, `permissions.py`) |
| FR-13 | Role-scoped Dashboards (3 active portals) | P0 | ✅ Implemented (`dashboards.py`, frontend) |
| FR-14 | CSV / PDF export of attendance & reports | P1 | ✅ Implemented (`export.py`, `reports.py`) |
| FR-15 | Student face enrollment (single & batch) | P0 | ✅ Implemented (`enroll.py`) |

---

## 6. Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-01 | Recognition latency | <2 seconds per image on CPU |
| NFR-02 | API response time | <500ms for non-vision endpoints |
| NFR-03 | Concurrent users | 5 simultaneous (pilot) |
| NFR-04 | Data retention | Full semester (90 days minimum) |
| NFR-05 | Uptime | Development environment — no SLA |
| NFR-06 | Security | bcrypt passwords, JWT auth, no plaintext secrets |

---

## 7. Constraints

| # | Constraint | Impact |
|---|---|---|
| C-1 | No GPU available | Must use CPU-optimized models (ONNX Runtime) |
| C-2 | No cloud infrastructure | Runs on developer laptop only |
| C-3 | No real student outcome data | ML trained on synthetic data only |
| C-4 | 3-month timeline, 4 students | Ruthless prioritization required |
| C-5 | No college data partnership yet | Cannot validate ML on real outcomes |
| C-6 | Single classroom pilot | No multi-tenant architecture needed |

---

## 8. Assumptions

| # | Assumption | Fallback if Wrong |
|---|---|---|
| AS-1 | InsightFace runs on CPU with ONNX Runtime | Fall back to dlib (slower, less accurate) |
| AS-2 | 30 students = brute-force cosine sim is fast enough | Add FAISS if >100 students |
| AS-3 | Single image per API call is acceptable | Add batch endpoint if needed |
| AS-4 | SQLite is sufficient for pilot | PostgreSQL ready via same SQLAlchemy models |
| AS-5 | Team members can serve as test enrollment subjects | Otherwise use LFW/public datasets |
| AS-6 | Synthetic training data validates pipeline correctness | Real accuracy requires real outcomes |
