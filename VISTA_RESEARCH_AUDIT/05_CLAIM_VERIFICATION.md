# Document 5 — Claim Verification Matrix

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 6 (Publication-Ready Claim Verification)
**Basis:** `audit-claim-verification.md` (Phase 4), `CLAIMS_TABLE.md`, direct source inspection.

**Evidence classification key:**
- **[VERIFIED]** — claim matches a present, internally-consistent artifact AND (where attempted) reproduces.
- **[PARTIALLY VERIFIED]** — claim is documented consistently and/or matches an artifact, but supporting reproducible code/data is absent, trivial, or incomplete.
- **[DOCUMENTED ONLY]** — claim is stated in documentation but lacks empirical artifact or code support.
- **[UNVERIFIED]** — no supporting artifact or code could be located.
- **[OUTDATED]** — the figure was correct for an earlier experiment/dataset but no longer reflects the current state.
- **[CONTRADICTED]** — a present artifact/code shows a different value for the same experiment.

---

## 1. Claim Verification Matrix

| # | Claim | Source Location | Evidence Found | Classification | Safe to Publish? | Notes |
|---|-------|----------------|---------------|----------------|-----------------|-------|
| C1 | Face recognition 100% on 14 samples | `README.md`, `AUDIT.md` §3, `REPORT.md`, `NEEDS_YOUR_INPUT.md` | Manual feasibility note in `AUDIT.md`; no eval script, no per-image results, no labeled test set | [PARTIALLY VERIFIED] | **Yes, with caveat** | Must be labeled "feasibility check (2 students, 14 images)" — never alongside 202-crop or 90.10% as comparable accuracy |
| C2 | Cosine-only accuracy 77.72% (FRR 16.83%) | `cascade_ablation.json`, `CLAIMS_TABLE.md` C-10, `paper/PAPER.md` | Artifact present; math confirmed (TP=157, FP=11, FN=34); generator script missing | [VERIFIED] (reproducibility PARTIAL) | **Yes** | State closed-set nature; note generator absent for reproducibility |
| C3 | Two-stage cascade accuracy 92.57% (FRR 1.98%) | `cascade_ablation.json`, `CLAIMS_TABLE.md` C-11, `paper/PAPER.md` | Artifact present; cascade logic verified in `recognize.py`; math confirmed (TP=187, FP=11, FN=4); generator missing | [VERIFIED] (reproducibility PARTIAL) | **Yes** | Strongest result. State: ablation uses NPZ prototypes, not production DB path. Generator absent. |
| C4 | XGBoost accuracy 95.7% / F1=0.957 | `AUDIT.md` §6, `vista/ml/CLAUDE.md`, `vista/README.md`, `vista/PROJECT_REPORT.md`, `vista/PLANB.md`, `docs_backup_final/ROADMAP.md` | Historical 200-row balanced dataset no longer exists; current eval gives 50% | [OUTDATED] | **No — REMOVE** | Must be removed from all docs where presented as current. Historical context only in `AUDIT.md`. |
| C5 | XGBoost accuracy 50% (current) | `risk_model_evaluation.json`, `CLAIMS_TABLE.md` C-19, `paper/PAPER.md` | Artifact present; **reproduced exactly** (acc=0.5, F1=0.3286, CM=[[0,3,9],[1,29,51],[0,36,71]]) | [VERIFIED] | **Yes** | Honest disclosure of below-baseline performance is appropriate |
| C6 | Majority-class baseline 53.5% | `CLAIMS_TABLE.md` C-20, `docs_backup_final/REPORT_ch7.md` | Reproduced (107/200=0.535); class counts confirmed | [VERIFIED] | **Yes** | Correctly contextualizes XGBoost as below baseline |
| C7 | Synthetic academic dataset of 1,000 samples | `CLAIMS_TABLE.md` C-18, `AUDIT.md`, `generate_sample_data.py` | 1000 rows confirmed; generator present but out of sync (200 rows, different labels) | [VERIFIED] (with reproducibility caveat) | **Yes** | Note: committed generator cannot reproduce the CSV; running it would corrupt data |
| C8 | 202 test crops & 20 enrolled identities | `cascade_ablation.json`, `CLAIMS_TABLE.md` C-10/C-11 | 202 & 20 confirmed by artifact arithmetic and NPZ inspection; generator missing | [VERIFIED] (reproducibility PARTIAL) | **Yes** | State closed-set; no impostor set |
| A1 | ResNet-50 test accuracy 90.10% (Split B, 101 samples) | `README.md`, `CLAIMS_TABLE.md`, `results_npz_splitB.txt` | Confirmed: test acc 0.9010, 101 test samples, val 93.07%, per-class weaknesses noted | [VERIFIED] | **Yes** | PyTorch seed not set — minor reproducibility risk |
| A2 | Latency: SCRFD+ArcFace 71.23ms; ResNet-50 32.5ms; cosine 1.07ms | `CLAIMS_TABLE.md` C-13, `latency_benchmark.json` | Confirmed in artifact (71.23, 32.5/30.8, 1.0693) | [VERIFIED] | **Yes** | Single-run, no CIs |
| A3 | Group-photo latency 77ms→311ms (1→45 faces) | `CLAIMS_TABLE.md` C-12 | Artifact confirmed, BUT values are **analytically extrapolated** from component benchmarks, not directly timed | [PARTIALLY VERIFIED] | **Yes, with caveat** | Change "Measured" to "Modeled" or "Extrapolated from component benchmarks" |
| A4 | AI coach groundedness 100% (10/10) | `CLAIMS_TABLE.md` C-31, `coach_groundedness.json` | Artifact confirms 10/10; not independently re-run (needs API key) | [PARTIALLY VERIFIED] | **Yes, with caveat** | State narrow scope: 10 queries, 1 student, no adversarial testing |
| A5 | 120 API routes; 27 tables; 3-role RBAC | `README.md`, `CLAIMS_TABLE.md` C-26/28/29, `AUDIT.md` | Confirmed programmatically in Phases 2-3 | [VERIFIED] | **Yes** | `vista/docs/IEEE_PAPER.md`'s 114/24/6 figures are superseded — do not cite that file |
| A6 | CIE policy thresholds (MAX=25, avg=20, best-2-of-3, absent≠0) | `CLAIMS_TABLE.md` C-25 | Confirmed in `cie_policy.py` (constants and logic match) | [VERIFIED] | **Yes** | |
| A7 | "21 students" in README | `README.md` Facial Pipeline section | Current `dataset/` has exactly 20 folders; 21st student (`1DA22AI010`) removed | [CONTRADICTED] | **No — FIX** | Update README to "20 students"; regenerate `image_count_report.txt` |
| A8 | Test suite pass count | `CLAIMS_TABLE.md` C-34 (27), `audit-inspection.md` (63) | Different scopes: C-34 runs 2 test files (27); 63 includes broader suite | [VERIFIED] | **Yes** | Align documented number with intended scope |

### Additional Claims from Paper (Inspected)

| # | Claim | Source | Classification | Safe? | Notes |
|---|-------|--------|---------------|-------|-------|
| P1 | Liveness uses EAR (Eye Aspect Ratio) | `PAPER.md` Section IV-A formula | [CONTRADICTED] | **No — FIX** | `liveness.py` does NOT compute EAR. Only uses det_score, face width, Laplacian variance. Remove EAR from paper formula. |
| P2 | ResNet-50 head: FC(2048→512)→ReLU→Dropout(0.3)→FC(512→20) | `PAPER.md` Section IV-A, `CLAIMS_TABLE.md` C-04 | [PARTIALLY VERIFIED] | **Yes, with correction** | Actual code adds BatchNorm1d at 2048 and 512, plus Dropout(0.4). Functionally equivalent, more regularized. Update description. |
| P3 | No PII sent to LLM | `PAPER.md` Section IX, `coach_service.py` | [VERIFIED] | **Yes** | `_call_openrouter()` sends only `facts` dict (numerical aggregates) labeled "NO PII" |
| P4 | Data leakage prevention guarantee | `PAPER.md` Section IV-A-4 | [VERIFIED] | **Yes** | `train_from_npz.py` `assert_no_leakage` verified; split on source-image IDs |
| P5 | DPDP Act 2023 compliance | `PAPER.md` Section IX | [DOCUMENTED ONLY] | **Yes, with caveat** | Consent form exists but has placeholder fields; no signed approvals in repo; consent form contradicts implementation (see Document 7) |
| P6 | "Photos deleted after processing" | `CONSENT_FORM.md` | [CONTRADICTED] | **No — REMOVE/FIX** | ~1.94 GB of raw photos retained in `dataset/` |
| P7 | "Face embedding stored in encrypted database" | `CONSENT_FORM.md` | [CONTRADICTED] | **No — REMOVE/FIX** | SQLite stores embeddings as plaintext JSON, no encryption at rest |

---

## 2. Claims That Must Be REMOVED from Any Paper Submission

| Claim | Where It Appears | Why | Evidence |
|-------|-----------------|-----|---------|
| XGBoost accuracy 95.7% / F1=0.957 (presented as current) | `vista/ml/CLAUDE.md`, `vista/README.md`, `vista/PROJECT_REPORT.md` ("✅ Production"), `vista/PLANB.md`, `docs_backup_final/ROADMAP.md` | Outdated — from a 200-row balanced dataset that no longer exists. Current result is 50.0% / 0.3286. | [OUTDATED — `audit-claim-verification.md` Claim 4, DC-1] |
| Liveness uses EAR (Eye Aspect Ratio) | `PAPER.md` Section IV-A | `liveness.py` does NOT compute EAR. Only det_score, face width, Laplacian variance. | [CONTRADICTED — `audit-inspection.md` D-3] |
| "21 students" in facial pipeline section | `README.md` | Current `dataset/` has exactly 20 folders. 21st student removed. | [CONTRADICTED — `audit-claim-verification.md` A7, DC-6] |
| "Photos deleted after processing" | `CONSENT_FORM.md` | ~1.94 GB of raw photos retained in `dataset/` | [CONTRADICTED] |
| "Face embedding stored in encrypted database" | `CONSENT_FORM.md` | SQLite is plaintext, no encryption at rest | [CONTRADICTED] |
| 100% on 14-image pilot (presented as comparable accuracy) | Anywhere alongside 202-crop or 90.10% results | Statistically trivial 2-class/14-image feasibility check with no script | [PARTIALLY VERIFIED — keep only as labeled "feasibility check"] |

---

## 3. Claims Safe to Publish with Current Evidence

| Claim | Evidence | Required Caveat |
|-------|---------|-----------------|
| Cascade accuracy 92.57%, FRR 1.98% (N=202, 20 classes) | [VERIFIED] | State: closed-set, NPZ prototype gallery (not production DB path), generator script absent, no formal hypothesis test |
| Cosine-only accuracy 77.72%, FRR 16.83% | [VERIFIED] | State: closed-set |
| ResNet-50 test accuracy 90.10% (Split B, 101 samples) | [VERIFIED] | State: PyTorch seed not explicitly set |
| XGBoost accuracy 50.0%, Macro F1 0.3286 (below 53.5% baseline) | [VERIFIED — reproduced] | State: synthetic data, circular labels, production uses rule engine not XGBoost |
| Majority-class baseline 53.5% | [VERIFIED — reproduced] | — |
| Latency: SCRFD+ArcFace 71.23ms, ResNet-50 32.5ms | [VERIFIED] | State: single-run, no CIs |
| Group-photo latency 77ms→311ms | [PARTIALLY VERIFIED] | Change "Measured" to "Modeled/extrapolated from component benchmarks" |
| 120 API routes, 27 tables, 3-role RBAC | [VERIFIED] | — |
| CIE policy thresholds | [VERIFIED] | — |
| Coach groundedness 10/10, 0 hallucinations | [PARTIALLY VERIFIED] | State: 10 queries, 1 student, no adversarial testing, narrow scope |
| No PII sent to LLM | [VERIFIED] | — |
| Data leakage prevention in ResNet-50 training | [VERIFIED] | — |
| Synthetic dataset of 1,000 samples | [VERIFIED] | State: generator out of sync with CSV; synthetic only, no real outcomes |

---

## 4. Claims Requiring Additional Experiments Before Publication

| Claim | Missing Experiment | Priority | Evidence |
|-------|-------------------|---------|---------|
| Open-set FAR (impostor rejection) | Create impostor test set with un-enrolled faces; evaluate cascade rejection rate | **Critical** | [UNVERIFIED — `CLAIMS_TABLE.md` C-16] |
| Cascade ablation reproducibility | Commit the missing cascade ablation generator script | **Critical** | [PARTIALLY VERIFIED — `audit-claim-verification.md` DC-4] |
| Demographic fairness | Evaluate recognition accuracy across skin tones, gender, lighting conditions | **High** | [UNVERIFIED — paper acknowledges gap] |
| Risk model on real longitudinal data | Train and evaluate on actual student outcome data, not synthetic | **High** | [VERIFIED — current data is synthetic] |
| Class-weighted XGBoost retraining | Add `scale_pos_weight` or class weights; re-evaluate LOW class | **Medium** | [VERIFIED — LOW F1=0.000] |
| Cross-validation for risk model | k-fold CV instead of single 80/20 split | **Medium** | [VERIFIED — single split only] |
| Formal hypothesis test for cascade | McNemar's test for paired proportions (cosine vs. cascade) | **Medium** | [VERIFIED — only Wilson CIs] |
| Adversarial coach testing | Prompt injection and adversarial queries beyond 10 benign | **Medium** | [PARTIALLY VERIFIED] |
| Deterministic threshold sweep | Replace `hash()` with seeded split; re-run | **High** | [VERIFIED — non-deterministic, DC-5] |

---

## 5. Recommended Language Adjustments for Borderline Claims

### C1: 14-Image Pilot

**Current (problematic):** "Face recognition: 100% on 14-image test set"
**Recommended:** "Feasibility check: 100% recognition on a 2-student, 14-image pilot (not a statistical evaluation)"
**Rationale:** 2 classes / 14 images is trivially solvable; cannot be compared to 202-crop or 90.10% results. [PARTIALLY VERIFIED]

### C4: XGBoost 95.7%

**Current (problematic):** "XGBoost selected (macro F1 = 0.957)" — presented as current
**Recommended:** "Historical pilot: XGBoost achieved macro F1 = 0.957 on a 200-row balanced synthetic set. Current evaluation on 1,000-row imbalanced data yields macro F1 = 0.3286 (below majority baseline)."
**Rationale:** 0.957 is from a dataset that no longer exists. [OUTDATED — `audit-claim-verification.md` DC-1]

### A3: Group-Photo Latency

**Current (problematic):** "Measured on Intel Core i7-13700H CPU" (for group scaling)
**Recommended:** "Modeled from component-level benchmarks on Intel Core i7-13700H CPU using linear scaling: `fast_path_ms = base_det_time + face_count × per_face_overhead`"
**Rationale:** Values are analytically extrapolated, not directly timed per face count. [PARTIALLY VERIFIED — DC-7]

### A4: Coach Groundedness

**Current (problematic):** "100% groundedness accuracy"
**Recommended:** "10 of 10 factual stress queries on a single student's records produced zero numerical hallucinations (narrow scope: 10 queries, 1 student, no adversarial testing)"
**Rationale:** Scope is too narrow for strong generalization. [PARTIALLY VERIFIED]

### P1: Liveness EAR

**Current (problematic):** Formula includes `EAR > γ_blink` in paper Section IV-A
**Recommended:** Remove EAR term. Replace with: "Liveness = (det_score ≥ 0.5) ∧ (face_width ≥ 50px) ∧ (Laplacian_variance ≥ 20.0)"
**Rationale:** `liveness.py` does not compute EAR. [CONTRADICTED — `audit-inspection.md` D-3]

### P5: DPDP Act Compliance

**Current (problematic):** "VISTA complies with India's Digital Personal Data Protection Act, 2023 through explicit consent capture"
**Recommended:** "VISTA is designed for DPDP Act 2023 alignment with a consent form template; however, institutional ethics approval and signed consent records require verification before deployment."
**Rationale:** Consent form has placeholder fields; no signed records in repo. [DOCUMENTED ONLY]

---

*End of Document 5 — Claim Verification Matrix*
