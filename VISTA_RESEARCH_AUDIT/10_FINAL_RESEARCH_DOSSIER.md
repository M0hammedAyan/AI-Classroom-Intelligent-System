# Document 10 — Final Research Dossier

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 7 (Final Research Dossier)
**Purpose:** Standalone executive briefing for the research team.

---

## Executive Summary

VISTA is an integrated, on-premise academic intelligence platform that connects face-recognition-based classroom attendance, academic risk scoring with explainability, and a fact-grounded AI study coach into a single web application. The system is fully implemented (120 API routes, 27 database tables, 3-role RBAC, React frontend, FastAPI backend) and has been evaluated with real and synthetic data. [VERIFIED — `audit-inspection.md` confirms full implementation; `audit-inventory.md` confirms component inventory]

The project's strongest contribution is a two-stage face recognition cascade (ArcFace cosine matching → ResNet-50 fallback) that reduces the false reject rate from 16.83% to 1.98% without increasing the false accept rate (5.45%) on 202 test crops across 20 enrolled students. [VERIFIED — `cascade_ablation.json`, math confirmed]

The project faces significant challenges for IEEE publication: missing ethics approval documentation, a missing cascade ablation generator script, pilot-scale evaluation (20 students, closed-set only), a risk model that performs below the majority-class baseline, and several factual contradictions between documentation and implementation. [VERIFIED — documented in Documents 5, 7, 8]

---

## 1. Verified Research Identity

**What VISTA actually is (based on evidence):**

VISTA is an integrated intelligent education system — not pure ML research and not pure software engineering. It combines existing, well-established open-source components (InsightFace SCRFD+ArcFace, ResNet-50, XGBoost, SHAP, FastAPI, React) into a working classroom platform with empirical evaluation of one specific architectural choice (the two-stage cascade). [VERIFIED — all components inspected in source code]

**What problem it solves:**
The operational disconnect between passive attendance tracking and timely academic advising. In traditional settings, attendance records are isolated from assessment analytics until semester examinations, delaying identification of at-risk students. VISTA integrates attendance (via face recognition), risk scoring (via rule engine + XGBoost/SHAP), and AI coaching (via LLM with deterministic firewall) into a single auditable platform. [DOCUMENTED ONLY — paper framing; no empirical comparison to specific deployed systems]

**Users:**
Three roles: Admin (full system management), Teacher (attendance marking, score entry), Student (read-only dashboard, AI coach chat). 20 actual AI&ML department students are enrolled. [VERIFIED — `auth.py`, `permissions.py`, `dataset/` directory]

**Primary classification:** Integrated intelligent education system with pilot-scale empirical evaluation. [VERIFIED — supported by full repository structure]

---

## 2. Technical Contributions (with Evidence Classifications)

| Contribution | Evidence Classification | Strength |
|-------------|------------------------|----------|
| Two-stage cascade (ArcFace + ResNet-50 fallback) | [VERIFIED] — ablation artifact present, math confirmed, cascade logic in `recognize.py`; [PARTIALLY VERIFIED] — generator script missing | **Moderate** |
| Deterministic computation firewall (LLM coach) | [VERIFIED] — code verified, PII stripped; [PARTIALLY VERIFIED] — 10/10 groundedness on narrow scope | **Low-Moderate** |
| CIE policy engine (VTU rules) | [VERIFIED] — `cie_policy.py` implements full logic | **Low** (engineering) |
| SCRFD + ArcFace vision pipeline | [VERIFIED] — standard InsightFace usage, off-the-shelf | **None** (not novel) |
| XGBoost risk model | [VERIFIED] — implemented but below baseline (50% < 53.5%) | **Negative result** |
| SHAP explainability | [VERIFIED] — standard TreeExplainer usage | **None** (not novel) |
| FastAPI + React platform | [VERIFIED] — 120 routes, 27 tables, 3-role RBAC | **Engineering** |
| Data leakage prevention in training | [VERIFIED] — `assert_no_leakage` in `train_from_npz.py` | **Good practice** |

---

## 3. Experimental Evidence Summary

### What Is Solid

| Result | Evidence | Reproducibility | Classification |
|--------|---------|----------------|---------------|
| Cascade FRR 16.83% → 1.98% (N=202) | `cascade_ablation.json` — math confirmed | Generator missing | [VERIFIED] (repro PARTIAL) |
| XGBoost Acc 50.0%, F1 0.3286 | `risk_model_evaluation.json` — reproduced exactly | Fully deterministic (rs=42) | [VERIFIED] |
| Majority baseline 53.5% | Derived from class distribution — reproduced | Fully deterministic | [VERIFIED] |
| 120 routes, 27 tables, 3-role RBAC | Confirmed programmatically | — | [VERIFIED] |
| ResNet-50 test acc 90.10% (Split B) | `results_npz_splitB.txt` | sklearn rs=42; PyTorch seed not set | [VERIFIED] (seed caveat) |
| Data leakage prevention | `assert_no_leakage` code verified | Code present | [VERIFIED] |
| No PII sent to LLM | `coach_service.py` — facts dict only, labeled "NO PII" | Code verified | [VERIFIED] |

### What Is Weak

| Result | Issue | Classification |
|--------|-------|---------------|
| Cascade ablation | Generator script missing — cannot reproduce from code | [PARTIALLY VERIFIED] |
| Threshold sweep (N=107) | Non-deterministic `hash()` split — fresh run gives different results | [PARTIALLY VERIFIED] |
| Latency group scaling | Analytically extrapolated, not directly measured | [PARTIALLY VERIFIED] |
| Coach groundedness 10/10 | Only 10 queries, 1 student, no adversarial testing | [PARTIALLY VERIFIED] |
| Synthetic risk data | Circular labels, generator out of sync with CSV | [VERIFIED] but circular/contradicted |
| `generate_sample_data.py` | Script produces 200 rows; CSV has 1000; different label logic | [CONTRADICTED] |

### What Is Missing

| Gap | Impact | Classification |
|-----|--------|---------------|
| Open-set impostor testing | FAR does not measure unknown-identity rejection | [UNVERIFIED] |
| Demographic fairness evaluation | Cannot assess bias across skin tones, gender | [UNVERIFIED] |
| Real longitudinal risk data | Risk model not validated against actual outcomes | [UNVERIFIED] |
| Institutional ethics approval | Publication blocker for biometric research | [UNVERIFIED] |
| Signed consent forms | No evidence of informed consent | [UNVERIFIED] |
| Formal hypothesis test for cascade | Statistical significance not established | [VERIFIED — only Wilson CIs] |
| Cross-validation for risk model | Single 80/20 split only | [VERIFIED] |
| Multi-institution evaluation | Single classroom, 20 students | [VERIFIED] |

---

## 4. Unresolved Issues and Risks

### Critical Risks

1. **No documented ethics approval.** The consent form has placeholder fields (`[Guide Name]`, `[Department/Faculty Committee Name]`). No IRB approval letter, no signed consent forms. For biometric data research, this is a **publication blocker**. [UNVERIFIED — `CONSENT_FORM.md` has placeholders]

2. **Consent form contradicts implementation.** The consent form claims photos are "deleted after processing" (photos are retained in `dataset/`, ~1.94 GB), the database is "encrypted" (SQLite is plaintext), 3-5 photos are collected (actual: 27-41 per student), and data is retained for 12 weeks (retained indefinitely). [CONTRADICTED — multiple contradictions documented in Document 7]

3. **Cascade ablation generator missing.** The project's strongest result (FRR 16.83% → 1.98%) cannot be reproduced from code. The `cascade_ablation.json` artifact exists and its math is verified, but the generating script is absent. [PARTIALLY VERIFIED — `audit-claim-verification.md` DC-4]

4. **Outdated 0.957 F1 claim.** Multiple documents (`vista/ml/CLAUDE.md`, `vista/README.md`, `vista/PROJECT_REPORT.md`, `vista/PLANB.md`) present XGBoost F1=0.957 as current performance. This is from a historical 200-row balanced dataset that no longer exists. The current result is 0.3286 (50% accuracy, below baseline). [OUTDATED — `audit-claim-verification.md` DC-1]

5. **Paper contains factual errors.** The liveness formula references EAR (Eye Aspect Ratio), but the code does not compute EAR. The "21 students" reference is stale (current dataset has 20). [CONTRADICTED — `audit-inspection.md` D-3, D-6]

### High-Priority Risks

6. **Non-deterministic threshold sweep.** The `evaluate_recognition.py` split uses `hash(src) % 100` which is non-deterministic across Python processes. A fresh run produced different metrics. [VERIFIED — `audit-claim-verification.md` DC-5]

7. **Generator out of sync with dataset.** `generate_sample_data.py` produces 200 rows with different label logic; the committed CSV has 1000 rows. Running the script would corrupt the dataset. [CONTRADICTED — DC-3]

8. **No demographic fairness evaluation.** For a biometric system in education, the absence of any fairness analysis is a significant ethical and scientific gap. [VERIFIED — paper acknowledges in Section VIII]

9. **Risk model below baseline.** XGBoost (50%) < majority baseline (53.5%). While honestly disclosed, this weakens the "Explainable Risk-Scoring" title framing. [VERIFIED]

10. **No data encryption at rest.** Biometric embeddings stored as plaintext JSON in SQLite. [VERIFIED — no encryption in `db.py`]

### Medium-Priority Risks

11. **In-memory token blocklist.** Revoked JWT tokens work after server restart. [VERIFIED — pilot-grade only]
12. **Insecure JWT secret fallback.** Falls back to hardcoded default if env var not set. [VERIFIED]
13. **No deletion API.** Consent form promises deletion on request; no endpoint exists. [UNVERIFIED]
14. **Multiple stale database copies.** Three copies of `vista_dev.db` at different locations/sizes. [VERIFIED]
15. **Tracker not wired.** ByteTrack tracker implemented but not connected to attendance routes. [VERIFIED — D-5]

---

## 5. Publication Readiness Verdict

**Overall score: 4/10.**

VISTA is a working, honestly-documented pilot system with one strong result (the cascade ablation) but significant reproducibility, ethical, and scale gaps. It is not ready for journal submission in its current state. A conference paper (workshop or short paper) is feasible with targeted revisions. [DOCUMENTED ONLY — holistic assessment based on all evidence]

### Blocking Issues (must resolve before ANY submission):
1. Obtain institutional ethics approval and document it. [UNVERIFIED]
2. Collect signed consent forms from all students. [UNVERIFIED]
3. Correct the consent form to match actual data practices. [CONTRADICTED]
4. Commit the cascade ablation generator script. [PARTIALLY VERIFIED]
5. Remove outdated 0.957 F1 claims from all documents. [OUTDATED]
6. Fix the paper's liveness formula (remove EAR). [CONTRADICTED]
7. Fix "21 students" → "20 students" in README. [CONTRADICTED]

### Strengthening Issues (should resolve before submission):
8. Make threshold sweep deterministic. [VERIFIED — DC-5]
9. Reconcile `generate_sample_data.py` with `student_data.csv`. [CONTRADICTED — DC-3]
10. Add open-set impostor testing (or clearly document as limitation). [UNVERIFIED]
11. Add demographic fairness evaluation (or clearly document as limitation). [UNVERIFIED]
12. Change latency "Measured" to "Modeled/extrapolated" for group scaling. [PARTIALLY VERIFIED]

---

## 6. Prioritized Next Steps (Ordered by Impact on Publication Readiness)

| Priority | Action | Impact | Effort | Evidence |
|----------|--------|--------|--------|---------|
| 1 | Obtain and document institutional ethics approval | Unblocks submission | External (human) | [UNVERIFIED] |
| 2 | Collect and archive signed consent forms from all 20 students | Unblocks submission | External (human) | [UNVERIFIED] |
| 3 | Correct consent form to match actual data handling (photos, encryption, count, retention, LLM) | Removes contradictions | Low | [CONTRADICTED] |
| 4 | Commit cascade ablation generator script | Enables reproducibility of strongest result | Medium (write `evaluate_cascade.py`) | [PARTIALLY VERIFIED — DC-4] |
| 5 | Remove outdated 0.957 F1 from all docs where presented as current | Removes false claims | Low | [OUTDATED — DC-1] |
| 6 | Fix paper's liveness formula (remove EAR, use actual heuristic checks) | Corrects factual error | Low | [CONTRADICTED — D-3] |
| 7 | Fix README "21 students" → "20 students" | Corrects stale reference | Trivial | [CONTRADICTED — D-6] |
| 8 | Make threshold sweep deterministic (replace `hash()` with seeded split) | Enables reproducibility | Low | [VERIFIED — DC-5] |
| 9 | Reconcile `generate_sample_data.py` with `student_data.csv` (N=1000, correct labels) | Prevents dataset corruption | Low | [CONTRADICTED — DC-3] |
| 10 | Add open-set impostor evaluation (or document as explicit limitation) | Strengthens security claims | Medium (create impostor test set) | [UNVERIFIED — C-16] |
| 11 | Add demographic fairness evaluation (or document as explicit limitation) | Addresses ethical gap | Medium-High | [UNVERIFIED] |
| 12 | Change latency wording from "Measured" to "Modeled" for group scaling | Corrects imprecision | Trivial | [PARTIALLY VERIFIED — DC-7] |
| 13 | Add McNemar's test for cascade ablation significance | Strengthens statistical rigor | Low | [VERIFIED — only CIs] |
| 14 | Try class-weighted XGBoost retraining | May improve LOW class performance | Low | [VERIFIED — LOW F1=0.000] |
| 15 | Add k-fold cross-validation for risk model | Strengthens evaluation | Low | [VERIFIED — single split] |
| 16 | Add adversarial coach testing (prompt injection) | Strengthens security claims | Medium | [PARTIALLY VERIFIED] |
| 17 | Set PyTorch seed explicitly in `train_from_npz.py` | Ensures full reproducibility | Trivial | [PARTIALLY VERIFIED] |
| 18 | Add data deletion API (consent form promises deletion on request) | Fulfills consent obligation | Low | [UNVERIFIED] |
| 19 | Add encryption at rest for biometric data | Addresses privacy concern | Medium | [VERIFIED — plaintext] |
| 20 | Add integrated classroom systems to literature review | Fills literature gap | Low (research) | [DOCUMENTED ONLY] |

---

## 7. Recommended IEEE Submission Strategy

### Step 1: Resolve Blocking Issues (Priorities 1-7)

Before any submission, the team MUST:
1. Obtain institutional ethics approval. This is the single most important action — without it, no reputable venue will accept biometric data research. [UNVERIFIED]
2. Collect signed consent forms. [UNVERIFIED]
3. Correct the consent form. [CONTRADICTED]
4. Commit the cascade ablation generator. [PARTIALLY VERIFIED]
5. Remove outdated claims and fix factual errors. [OUTDATED/CONTRADICTED]

### Step 2: Strengthen Evidence (Priorities 8-12)

Make the threshold sweep deterministic, reconcile the generator, add open-set/fairness evaluation (or document as limitations), and correct latency wording.

### Step 3: Choose Target Venue

**Recommended primary target:** IEEE conference focused on educational technology (TAL, FIE, or ICALT). These venues are more accepting of systems/integration papers with pilot-scale evaluation. [DOCUMENTED ONLY — venue recommendation]

**Alternative:** IEEE Access (open-access journal) if the team prefers a journal format. IEEE Access has broader scope and may accept systems papers with moderate experimental rigor. [DOCUMENTED ONLY]

**Not recommended:** Top-tier ML/CV venues (NeurIPS, CVPR, ICCV) or high-impact IEEE journals (TPAMI, TLT) — the evaluation scale and algorithmic novelty are insufficient. [VERIFIED — pilot scale, standard techniques]

### Step 4: Frame the Paper Honestly

The paper should be framed as a **practical systems paper** demonstrating that on-premise edge vision + explainable risk scoring + grounded LLM coaching can operate cohesively, with the cascade ablation as the primary quantitative contribution. It should NOT be framed as an algorithmic breakthrough or as achieving superior ML performance. [VERIFIED — based on evidence classifications throughout this audit]

**Recommended title:** "VISTA: A Two-Stage Cascade Approach for On-Premise Classroom Face Recognition with Integrated Explainable Risk Scoring" — this foregrounds the strongest contribution while being honest about the integration nature. [DOCUMENTED ONLY — recommendation]

**Key framing points:**
- Lead with the cascade ablation (strongest, most defensible result). [VERIFIED]
- Honestly disclose XGBoost below baseline; explain that production uses the rule engine. [VERIFIED]
- Frame the LLM coach groundedness as a narrow pilot (10 queries), not a generalizable claim. [PARTIALLY VERIFIED]
- Explicitly state all limitations (closed-set, 20 students, synthetic data, heuristic liveness, no fairness eval). [VERIFIED — paper already does this well in Section VIII]
- Document ethics approval and consent procedures (once obtained). [UNVERIFIED — currently missing]

### Step 5: Submit and Iterate

Submit to the chosen venue, incorporating reviewer feedback. If rejected, address reviewer concerns (likely: open-set testing, scale, fairness) and resubmit. The cascade ablation is the most likely result to survive peer review; the risk model and coach evaluation are the most likely to be criticized. [DOCUMENTED ONLY — submission strategy]

---

*End of Document 10 — Final Research Dossier*
