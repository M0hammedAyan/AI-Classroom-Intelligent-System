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

### In Scope (Pilot)

- Single classroom (CSE-3A), 20–30 students
- Face detection + recognition from uploaded images
- Attendance recording with confidence scores
- Manual attendance override by teachers
- Rule-based + XGBoost risk scoring
- Template-based explainable reasons
- React dashboard with login, attendance log, risk flags
- CSV export of attendance reports
- JWT authentication (admin/teacher roles)

### Out of Scope (Phase 2+)

- Multi-classroom / multi-college support
- Video stream processing / ByteTrack tracking
- Real-time alerts / WebSocket push
- LMS integration for score ingestion
- SHAP-based model explanations
- Separate dashboards per role (mentor/HOD/student)
- Cloud deployment / Kubernetes
- Edge device deployment (Raspberry Pi/Jetson)
- Supervised ML trained on real outcome labels
- Token refresh endpoint
- PDF export

---

## 4. User Roles

| Role | Permissions | Pilot Status |
|---|---|---|
| Admin | All access + risk recompute + user management | ✅ Implemented |
| Teacher | View attendance, risk flags, override records, export | ✅ Implemented |
| Mentor | View assigned students' risk trends | ❌ Phase 2 |
| HOD | Department-level analytics | ❌ Phase 2 |
| Student | View own attendance/risk | ❌ Phase 2 |

---

## 5. Functional Requirements

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-01 | Detect faces in classroom image | P0 | ❌ Not built |
| FR-02 | Extract 512-dim face embeddings (ArcFace) | P0 | ❌ Not built |
| FR-03 | Match embeddings via cosine similarity | P0 | ❌ Not built |
| FR-04 | Anti-spoofing liveness check | P1 | ❌ Not built |
| FR-05 | `recognize(image_path)` entry point | P0 | ❌ Not built |
| FR-06 | Mark attendance via image upload API | P0 | ✅ Implemented (vision stub) |
| FR-07 | Derive absent status at read time | P0 | ✅ Implemented |
| FR-08 | Manual attendance override | P1 | ✅ Implemented |
| FR-09 | Compute risk from attendance + scores | P0 | ✅ Implemented |
| FR-10 | Explainable reasons + recommendations | P0 | ✅ Implemented (template) |
| FR-11 | Admin-triggered risk recompute | P1 | ✅ Implemented |
| FR-12 | Role-gated JWT authentication | P0 | ✅ Implemented |
| FR-13 | Dashboard (attendance + risk overview) | P0 | ✅ Implemented |
| FR-14 | CSV export of attendance | P1 | ✅ Implemented |
| FR-15 | Student face enrollment | P0 | ❌ Not built |

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
