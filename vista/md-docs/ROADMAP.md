# VISTA — Development Roadmap

> **Last Updated:** 2026-06-24
> **Status:** Active — Milestone 1 is next.

---

## Milestone Summary

| # | Milestone | Status | Readiness Score |
|---|---|---|---|
| M0 | Project Planning & Documentation | ✅ Complete | 95/100 |
| M1 | Vision Pipeline (Face Recognition) | ✅ Complete | 95/100 |
| M2 | Student Enrollment Flow | ✅ Complete | 90/100 |
| M3 | End-to-End Integration Testing | ✅ Complete | 90/100 |
| M4 | SHAP Explainability | ✅ Complete | 90/100 |
| M5 | Multi-Face Detection & Tracking | ✅ Complete | 85/100 |
| M6 | Production Hardening | 🔄 In Progress | 80/100 (Docker + Postgres ready) |

---

## Dependency Graph

```
M0 (Planning) ✅
 │
 ▼
M1 (Vision Pipeline) ✅
 │
 ├──────────────────┐
 ▼                  ▼
M2 (Enrollment) ✅  M5 (Multi-Face & Tracking) ✅
 │
 ▼
M3 (E2E Testing) ✅
 │
 ▼
M4 (SHAP Explainer) ✅
 │
 ▼
M6 (Production Hardening & Pilot Deployment) 🔄
```

---

## Milestone 0: Project Planning ✅ COMPLETE

**Deliverables (all complete):**
- [x] PROJECT_PLAN.md
- [x] ARCHITECTURE.md
- [x] DATABASE_DESIGN.md
- [x] API_SPEC.md
- [x] ML_DESIGN.md
- [x] ROADMAP.md (this file)
- [x] All contract docs (API_CONTRACT, DB_SCHEMA, etc.)
- [x] Backend fully implemented
- [x] Frontend fully implemented
- [x] ML module fully implemented
- [x] Mock server operational

---

## Milestone 1: Vision Pipeline

**Objective:** Implement complete face recognition from image to student_id.

**Dependencies:** InsightFace + ONNX Runtime installed in venv.

**Deliverables:**

| Task | File | Effort | Priority |
|---|---|---|---|
| Install InsightFace + onnxruntime | requirements | 30 min | P0 |
| Face detection (SCRFD) | `vision/detect.py` | 3 hrs | P0 |
| Face embedding (ArcFace R50) | `vision/embed.py` | 3 hrs | P0 |
| Cosine similarity matching | `vision/match.py` | 2 hrs | P0 |
| Anti-spoofing (MiniFASNet or pass-through) | `vision/liveness.py` | 3 hrs | P1 |
| Pipeline orchestrator | `vision/recognize.py` | 2 hrs | P0 |
| Integration test with real photos | `vision/test_recognize.py` | 4 hrs | P0 |

**Acceptance Criteria:**
- `recognize(image_path)` returns correct student_id for enrolled faces
- Confidence > 0.5 for true matches
- Returns `student_id=None` for unknown faces
- Latency < 2 seconds per image on CPU

**Risks:**
- InsightFace may require specific ONNX Runtime version
- Model download on first run (~100MB)
- CPU inference may be slow without optimization

---

## Milestone 2: Student Enrollment Flow

**Objective:** Provide a way to register student faces in the system.

**Dependencies:** M1 complete (need embedding extraction working).

**Deliverables:**

| Task | File | Effort |
|---|---|---|
| Enrollment CLI tool | `vision/enroll_cli.py` | 2 hrs |
| Enrollment API endpoint | `backend/app/routes/enroll.py` | 3 hrs |
| Register route in main.py | `backend/app/main.py` | 15 min |
| Enroll team members (test data) | Manual process | 1 hr |

**Acceptance Criteria:**
- 3–5 images per student → averaged embedding stored in DB
- Re-enrollment overwrites existing embedding
- Error returned if no face detected in provided images

---

## Milestone 3: End-to-End Integration Testing

**Objective:** Prove the complete flow works: image → detection → recognition → DB → dashboard.

**Dependencies:** M1 + M2 complete, enrolled test subjects.

**Deliverables:**

| Task | Effort |
|---|---|
| Enroll 5 team members with 3–5 photos each | 1 hr |
| Capture separate test images (different day/lighting) | 1 hr |
| Submit test images via API, verify attendance records | 2 hrs |
| Verify dashboard displays correct data | 1 hr |
| Compute and document precision/recall/FAR | 2 hrs |
| Threshold sweep (0.45–0.65) to find optimal | 1 hr |

**Acceptance Criteria:**
- True Positive Rate ≥ 90% on test set
- False Accept Rate < 5%
- All metrics documented in INTEGRATION_LOG.md

---

## Milestone 4: SHAP Explainability

**Objective:** Replace template reasons with model-generated SHAP explanations.

**Dependencies:** ML module complete (already is); `shap` library installed.

**Deliverables:**

| Task | File | Effort |
|---|---|---|
| Install shap library | requirements | 10 min |
| Add TreeExplainer to risk_engine.py | `ml/risk_engine.py` | 3 hrs |
| Convert SHAP values → human reasons | `ml/risk_engine.py` | 3 hrs |
| Add SHAP waterfall to export | `backend/app/routes/export.py` | 4 hrs |
| Compare SHAP vs rule-based in tests | `ml/test_risk_engine.py` | 2 hrs |

**Acceptance Criteria:**
- SHAP reasons are human-readable (not raw feature names)
- Top 3 SHAP contributors match intuition (attendance most important)
- Both rule-based and SHAP paths available (toggle via config)

---

## Milestone 5: Multi-Face Detection (Optional)

**Objective:** Process single image with multiple faces, identify all students.

**Dependencies:** M1 complete.

**Deliverables:**

| Task | File | Effort |
|---|---|---|
| Modify recognize() to return list of results | `vision/recognize.py` | 3 hrs |
| Modify POST /attendance/mark to loop results | `backend/app/routes/attendance.py` | 2 hrs |
| Duplicate detection (same student twice) | Both | 2 hrs |

---

## Milestone 6: Production Hardening (Phase 2)

**Objective:** Make the system deployable beyond dev laptop.

| Task | Effort |
|---|---|
| Docker Compose (backend + frontend + db) | 4 hrs |
| PostgreSQL migration | 2 hrs |
| Environment variable management | 1 hr |
| Health check + monitoring | 2 hrs |
| Rate limiting on auth | 1 hr |

---

## Implementation Order (Strict)

```
1. ✅ Install dependencies (scikit-learn, xgboost, pandas) — DONE
2. ✅ Implement ML module (features.py, risk_engine.py, train.py) — DONE
3. ✅ Implement Backend routes (14 modules, 122 registered routes) — DONE
4. ✅ Implement Frontend pages (3 active role dashboards, Tailwind v4) — DONE
5. ✅ Install InsightFace + ONNX Runtime — DONE
6. ✅ Implement detect.py (SCRFD) — DONE
7. ✅ Implement embed.py (ArcFace R50) — DONE
8. ✅ Implement match.py (cosine matching, threshold 0.55) — DONE
9. ✅ Implement liveness.py (heuristic checks) — DONE
10. ✅ Implement recognize.py + personal_classifier.py — DONE
11. ✅ Write test_recognize.py (7 tests) — DONE
12. ✅ Implement enrollment (enroll.py + routes/enroll.py) — DONE
13. ✅ Run E2E integration test (facial_pipeline.py + backend) — DONE
14. ✅ Add SHAP explainer (vista/ml/explainer.py) — DONE
15. ✅ Document all metrics and sync docs — DONE
16. 🔄 Final pilot deployment preparation — IN PROGRESS
```

---

## Testing Strategy

| Layer | Method | Tool | Status |
|---|---|---|---|
| ML | 7 unit test cases | `test_risk_engine.py` | ✅ All 7 pass |
| Backend | 114 API endpoint routes | Tested via FastAPI TestClient / manual | ✅ All pass |
| Frontend | Build verification | `npm run build` | ✅ Passes |
| Vision | 7 unit & pipeline tests | `test_recognize.py` | ✅ All 7 pass |
| Model Benchmarks | Accuracy & macro F1 | Pilot set / Split B / Synthetic | ✅ Verified |

### Vision Test Protocol (for M3)
- Pilot evaluation: 14 test photos of 2 students (100% correct match)
- 20-class .npz split B model: 101 test samples (90.10% accuracy)
- Automated tests: 7 test cases in `vista/vision/tests/test_recognize.py`
- Thresholds: Default 0.55 cosine similarity (configurable via `VISTA_FACE_MATCH_THRESHOLD`)

---

## Risk Register

| # | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| R-1 | Real-world pilot dataset scale | MEDIUM | MEDIUM | Pilot tested on 21 enrolled students; expand across college |
| R-2 | Lighting & angle variance | MEDIUM | MEDIUM | Personal classifier fallback (`personal_classifier.py`) |
| R-3 | Synthetic ML data limitation | MEDIUM | LOW | Macro F1=0.957 validated on synthetic; UCI benchmark verified |
| R-4 | Parent notification delivery | LOW | MEDIUM | DB alert queue built; external Twilio/SendGrid credentials required |
