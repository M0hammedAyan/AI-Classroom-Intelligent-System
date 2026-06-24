# VISTA — Development Roadmap

> **Last Updated:** 2026-06-24
> **Status:** Active — Milestone 1 is next.

---

## Milestone Summary

| # | Milestone | Status | Readiness Score |
|---|---|---|---|
| M0 | Project Planning & Documentation | ✅ Complete | 95/100 |
| M1 | Vision Pipeline (Face Recognition) | ❌ Not started | 90/100 (ready) |
| M2 | Student Enrollment Flow | ❌ Not started | 85/100 |
| M3 | End-to-End Integration Testing | ❌ Not started | 80/100 |
| M4 | SHAP Explainability | ❌ Not started | 75/100 |
| M5 | Multi-Face Detection (Batch) | ❌ Not started | 70/100 |
| M6 | Production Hardening | ❌ Not started | 60/100 |

---

## Dependency Graph

```
M0 (Planning) ✅
 │
 ▼
M1 (Vision Pipeline) ← CRITICAL PATH
 │
 ├──────────────────┐
 ▼                  ▼
M2 (Enrollment)    M5 (Multi-Face) [optional]
 │
 ▼
M3 (E2E Testing)
 │
 ▼
M4 (SHAP) ← can run parallel after M3 starts
 │
 ▼
M6 (Production Hardening)
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
2. ✅ Implement ML module — DONE
3. ✅ Implement Backend routes — DONE
4. ✅ Implement Frontend pages — DONE
5. ❌ Install InsightFace + ONNX Runtime
6. ❌ Implement detect.py
7. ❌ Implement embed.py
8. ❌ Implement match.py
9. ❌ Implement liveness.py
10. ❌ Implement recognize.py
11. ❌ Write test_recognize.py
12. ❌ Implement enrollment (CLI + API)
13. ❌ Run E2E integration test
14. ❌ Add SHAP to risk_engine.py
15. ❌ Document all metrics
16. ❌ Final demo preparation
```

---

## Testing Strategy

| Layer | Method | Tool | Status |
|---|---|---|---|
| ML | 7 unit test cases | Custom runner | ✅ All pass |
| Backend | API endpoint tests | Tested manually | ✅ All pass |
| Frontend | Build verification | `npm run build` | ✅ Passes |
| Vision | Labeled test set | pytest (planned) | ❌ Blocked on M1 |
| E2E | Full flow test | Manual + documented | ❌ Blocked on M2 |

### Vision Test Protocol (for M3)
- Enrollment set: 3–5 photos per student (Day 1)
- Test set: 2–3 photos per student (Day 2+, different lighting)
- Metrics: Precision, Recall, FAR, TAR @ FAR=0.1%
- Threshold sweep: 0.45, 0.50, 0.55, 0.60, 0.65

---

## Risk Register

| # | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| R-1 | Vision module empty — blocks demo | CRITICAL | HIGH | Build immediately (M1) |
| R-2 | No real face data for testing | HIGH | HIGH | Enroll team members |
| R-3 | InsightFace version conflicts | MEDIUM | MEDIUM | Pin versions; test early |
| R-4 | XGBoost F1 not generalizable | MEDIUM | HIGH | Label as synthetic validation |
| R-5 | Scope creep (video/tracking/SHAP) | HIGH | MEDIUM | Strict milestone gates |
| R-6 | CPU inference too slow | MEDIUM | LOW | SCRFD + R50 = ~50ms; acceptable |
| R-7 | SHAP cited but not implemented | MEDIUM | HIGH | Either implement (M4) or remove claim |
