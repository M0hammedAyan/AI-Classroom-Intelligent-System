# Document 8 — IEEE Publication Assessment

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 7 (IEEE Publication Assessment)
**Basis:** All prior audit documents (01-07), `audit-claim-verification.md`, `paper/PAPER.md`, `PAPER_TODO.md`.

---

## 1. Is VISTA Genuinely Suitable for an IEEE Research Paper? (Honest Assessment)

**Answer: Conditionally yes — as a conference paper (short paper or workshop), not a full journal paper, and only with significant revisions.**

VISTA has a working, implemented integrated system with real evaluation artifacts. Its strongest result — the two-stage cascade ablation (FRR 16.83% → 1.98%, FAR unchanged) — is a legitimate, quantified architectural contribution with artifact support. [VERIFIED — `cascade_ablation.json`]

However, VISTA faces several fundamental challenges for IEEE publication:

1. **Primarily an integration project:** No new algorithm is proposed. All ML components use existing, pretrained models (SCRFD, ArcFace, ResNet-50, XGBoost, SHAP) as-is or with standard fine-tuning. [VERIFIED — off-the-shelf usage throughout]

2. **Pilot-scale evaluation:** 20 students, closed-set only, synthetic risk data. [VERIFIED — documented limitations]

3. **Missing ethics documentation:** No IRB approval, no signed consent, consent form contradicts implementation. [UNVERIFIED — critical gap]

4. **Reproducibility gaps:** The cascade ablation generator script is missing (the strongest result cannot be reproduced from code). [PARTIALLY VERIFIED]

5. **Below-baseline risk model:** XGBoost (50%) < majority baseline (53.5%). While honestly disclosed, this is a negative ML result that weakens the "explainable risk-scoring" framing. [VERIFIED]

**Bottom line:** The system is too integrated/engineering-focused for a top-tier ML venue, but the cascade ablation and deterministic computation firewall are defensible as a workshop or short conference paper focused on practical system design. [DOCUMENTED ONLY — editorial assessment based on evidence]

---

## 2. What Is the Strongest Research Contribution?

**The two-stage cascade for classroom face recognition (ArcFace cosine → ResNet-50 fallback).**

Evidence: [VERIFIED — `cascade_ablation.json`, cascade logic in `recognize.py`]
- Reduces FRR from 16.83% to 1.98% (−14.85pp)
- Does not increase FAR (5.45% → 5.45%)
- Recovers 30 of 34 cosine-rejected true probes
- Ablation is controlled (same 202-crop test set, same 20 classes)
- Wilson 95% CIs provided

This is the single most defensible quantitative result in the project. It demonstrates that adding a second-stage classifier specifically trained on the enrolled students can recover marginal cosine rejections without introducing false accepts. This is a practical architectural insight for classroom-scale deployments. [VERIFIED]

**Why it's the strongest:** It has artifact support, internally consistent math, a clear ablation comparison, and addresses a real operational problem (high FRR in classroom face recognition). [VERIFIED]

**Caveats that must be stated:**
- Generator script is missing (reproducibility PARTIAL) [PARTIALLY VERIFIED]
- Closed-set only (no impostor testing) [VERIFIED]
- 20 students only (pilot scale) [VERIFIED]
- No formal hypothesis test [VERIFIED — only Wilson CIs]
- Ablation uses NPZ prototype galleries, not production DB-gallery path [DOCUMENTED ONLY]

---

## 3. Which Contribution Has the Strongest Experimental Evidence?

**Ranking by evidence strength:**

| Rank | Contribution | Evidence Strength | Classification |
|------|-------------|-------------------|---------------|
| 1 | Two-stage cascade ablation (FRR improvement) | Artifact present, math verified, ablation controlled; generator missing | [VERIFIED] (reproducibility PARTIAL) |
| 2 | XGBoost risk model results (honest negative) | Artifact present, reproduced exactly in Phase 4, deterministic | [VERIFIED] |
| 3 | Majority-class baseline (53.5%) | Reproduced exactly, deterministic | [VERIFIED] |
| 4 | 120 endpoints / 27 tables / 3-role RBAC | Confirmed programmatically | [VERIFIED] |
| 5 | ResNet-50 test accuracy (90.10%, Split B) | Artifact present, per-class breakdown available | [VERIFIED] (seed not set) |
| 6 | Latency benchmarks (component-level) | Single-run artifact, no CIs | [PARTIALLY VERIFIED] |
| 7 | Coach groundedness (10/10) | Artifact present, narrow scope, requires API key | [PARTIALLY VERIFIED] |
| 8 | Data leakage prevention | Code verified (`assert_no_leakage`) | [VERIFIED] |
| 9 | Deterministic computation firewall | Code verified, groundedness test supports | [VERIFIED] (narrow eval) |
| 10 | 14-image pilot 100% | No script, no saved results | [PARTIALLY VERIFIED] |

---

## 4. Which Component Is Currently Weakest?

**The academic risk prediction system (XGBoost on synthetic data).**

Reasons: [VERIFIED — all points confirmed in source code and evaluation artifacts]
1. XGBoost accuracy (50.0%) is below the majority-class baseline (53.5%) — a negative ML result. [VERIFIED — reproduced]
2. Complete failure on minority class (LOW F1=0.000, 0/12 correct). [VERIFIED]
3. Training data is entirely synthetic with circular labels (derived from the same rule engine used in production). [VERIFIED]
4. Generator script is out of sync with the committed CSV (200 vs 1000 rows, different label logic). [CONTRADICTED]
5. No cross-validation — single 80/20 split only. [VERIFIED]
6. No class weighting to address imbalance. [VERIFIED]
7. No real longitudinal outcome data validates the predictions. [VERIFIED]
8. The production system correctly does NOT use XGBoost for actual risk decisions — it uses the deterministic rule engine. [VERIFIED — this is actually a strength of the system design, but means XGBoost contributes no operational value]

**Impact on the paper:** The paper title includes "Explainable Risk-Scoring" but the strongest risk-scoring component (the rule engine) is deterministic, not ML-based. The XGBoost+SHAP path is auxiliary and performs below baseline. This creates a framing tension — the "explainable" part is backed by SHAP (standard technique) but the "risk-scoring" ML model is a negative result. [VERIFIED — structural issue in paper framing]

---

## 5. Which Results Can Safely Be Published?

| Result | Safe to Publish? | Required Caveats | Evidence |
|--------|-----------------|-----------------|---------|
| Cascade: Acc 92.57%, FRR 1.98%, FAR 5.45% (N=202) | **Yes** | Closed-set; NPZ prototype gallery; generator absent; no hypothesis test | [VERIFIED] |
| Cosine-only: Acc 77.72%, FRR 16.83% | **Yes** | Closed-set; same caveats | [VERIFIED] |
| ResNet-50 test acc 90.10% (Split B, 101 samples) | **Yes** | PyTorch seed not set; 20 classes | [VERIFIED] |
| XGBoost: Acc 50.0%, F1 0.3286 (below 53.5% baseline) | **Yes** | Synthetic data; circular labels; below baseline; production uses rule engine | [VERIFIED — honest disclosure] |
| Latency: SCRFD+ArcFace 71.23ms, ResNet-50 32.5ms | **Yes** | Single-run, no CIs | [VERIFIED] |
| Group-photo latency 77→311ms | **Yes** | Change "Measured" to "Modeled/extrapolated" | [PARTIALLY VERIFIED] |
| Coach: 10/10 groundedness | **Yes** | 10 queries, 1 student, no adversarial testing | [PARTIALLY VERIFIED] |
| 120 routes, 27 tables, 3-role RBAC | **Yes** | — | [VERIFIED] |
| CIE policy thresholds | **Yes** | — | [VERIFIED] |
| 14-image pilot 100% | **Only as labeled feasibility check** | Never alongside 202-crop or 90.10% | [PARTIALLY VERIFIED] |
| XGBoost F1=0.957 | **No — REMOVE** | Outdated, from nonexistent dataset | [OUTDATED] |
| Liveness uses EAR | **No — FIX** | Code does not compute EAR | [CONTRADICTED] |
| "Photos deleted after processing" | **No — FIX** | Photos retained | [CONTRADICTED] |
| "Encrypted database" | **No — FIX** | SQLite plaintext | [CONTRADICTED] |
| "21 students" | **No — FIX** | Current dataset has 20 | [CONTRADICTED] |

---

## 6. Which Claims Must Be Removed?

1. **XGBoost F1=0.957 presented as current** — appears in `vista/ml/CLAUDE.md`, `vista/README.md`, `vista/PROJECT_REPORT.md`, `vista/PLANB.md`, `docs_backup_final/ROADMAP.md`. [OUTDATED — `audit-claim-verification.md` DC-1]

2. **Liveness uses EAR** — paper Section IV-A formula. [CONTRADICTED — `liveness.py` does not compute EAR]

3. **"21 students"** in README facial pipeline section. [CONTRADICTED — current `dataset/` has 20]

4. **"Photos deleted after processing"** in consent form. [CONTRADICTED — photos retained in `dataset/`]

5. **"Encrypted database"** in consent form. [CONTRADICTED — SQLite is plaintext]

6. **14-image pilot "100% accuracy" presented as comparable to cascade results** — must be relabeled as feasibility check only. [PARTIALLY VERIFIED]

7. **Any novelty claim for individual components** (SCRFD, ArcFace, XGBoost, SHAP used as-is are not novel). [VERIFIED — off-the-shelf usage]

---

## 7. What Additional Experiments Are Essential Before Submission?

| Experiment | Priority | Rationale | Evidence |
|-----------|---------|-----------|---------|
| **Commit cascade ablation generator script** | **Critical** | The project's strongest result cannot be reproduced from code | [PARTIALLY VERIFIED — DC-4] |
| **Open-set impostor testing** | **Critical** | FAR of 5.45% measures wrong-student matches, not unknown-identity rejection; security claims are unsupported without this | [UNVERIFIED — C-16] |
| **Document institutional ethics approval** | **Critical** | No IRB approval documented; publication blocker for biometric research | [UNVERIFIED] |
| **Collect signed consent forms** | **Critical** | Consent form template has placeholders; no signed copies | [UNVERIFIED] |
| **Make threshold sweep deterministic** | **High** | Replace `hash()` with seeded split; current results non-reproducible | [VERIFIED — DC-5] |
| **Reconcile `generate_sample_data.py` with CSV** | **High** | Running the committed script corrupts the dataset | [CONTRADICTED — DC-3] |
| **Demographic fairness evaluation** | **High** | Biometric systems without fairness analysis face ethical criticism | [UNVERIFIED — paper acknowledges] |
| **Class-weighted XGBoost retraining** | **Medium** | Current model fails on LOW class (F1=0.000); class weights may help | [VERIFIED] |
| **Cross-validation for risk model** | **Medium** | Single 80/20 split only; k-fold would strengthen claims | [VERIFIED] |
| **Formal hypothesis test for cascade** | **Medium** | McNemar's test for paired proportions | [VERIFIED — only Wilson CIs] |
| **Adversarial coach testing** | **Medium** | 10 benign queries is insufficient; add prompt injection tests | [PARTIALLY VERIFIED] |
| **End-to-end group photo latency (direct measurement)** | **Low** | Current values are extrapolated from component benchmarks | [PARTIALLY VERIFIED — DC-7] |

---

## 8. What Is the Minimum Work Required Before Submission?

**Tier 1 — Must Do (blocks submission):**
1. Commit the cascade ablation generator script (`evaluation/evaluate_cascade.py`). [PARTIALLY VERIFIED]
2. Remove/correct the 6 claims listed in Section 6 above. [VERIFIED — all contradictions documented]
3. Obtain and document institutional ethics approval. [UNVERIFIED]
4. Obtain and archive signed consent forms from all 20 students. [UNVERIFIED]
5. Correct the consent form to match actual data handling practices. [CONTRADICTED]
6. Fix the paper's liveness formula (remove EAR). [CONTRADICTED]

**Tier 2 — Should Do (strengthens paper significantly):**
7. Add open-set impostor evaluation (at minimum, document as limitation if not conducted). [UNVERIFIED]
8. Make the threshold sweep deterministic (replace `hash()` with seeded split). [VERIFIED — DC-5]
9. Reconcile `generate_sample_data.py` with `student_data.csv`. [CONTRADICTED — DC-3]
10. Update README "21 students" to "20 students". [CONTRADICTED]

**Tier 3 — Nice to Have (improves rigor):**
11. Add McNemar's test for cascade ablation significance. [VERIFIED — only Wilson CIs]
12. Try class-weighted XGBoost retraining. [VERIFIED — LOW F1=0.000]
13. Add k-fold cross-validation for risk model. [VERIFIED — single split]

---

## 9. Conference Paper vs. Journal Paper? Which Venues?

### Conference Paper: More Realistic

VISTA's contributions (cascade architecture, system integration, deterministic computation firewall) are better suited to a conference or workshop format because:
- The primary contribution is a systems/integration paper, not an algorithmic breakthrough. [VERIFIED]
- Evaluation is pilot-scale (20 students). [VERIFIED]
- The strongest result (cascade ablation) is a single experiment, not a comprehensive evaluation suite. [VERIFIED]
- Risk model is a negative result (below baseline). [VERIFIED]

### Recommended Target Venues

**IEEE Conferences (most appropriate):**

1. **IEEE International Conference on Teaching, Assessment, and Learning for Teaching (TAL)** — focused on educational technology, assessment, and learning. VISTA's attendance + risk + coaching integration fits. [DOCUMENTED ONLY — venue recommendation based on scope fit]

2. **IEEE Frontiers in Education Conference (FIE)** — educational engineering and methods. VISTA's classroom integration is relevant. [DOCUMENTED ONLY — venue recommendation]

3. **IEEE International Conference on Advanced Learning Technologies (ICALT)** — learning technologies and educational applications. VISTA's risk prediction + AI coach fit. [DOCUMENTED ONLY — venue recommendation]

4. **LAK (Learning Analytics and Knowledge)** — not IEEE but highly relevant; learning analytics focus. The project already cites a LAK paper (`Lee et al. 2024`). [DOCUMENTED ONLY — venue recommendation]

**IEEE Journals (more ambitious, requires more work):**

1. **IEEE Transactions on Learning Technologies (TLT)** — the project already cites a TLT paper (`Barata et al. 2023`). Would require significantly more experimental rigor (larger datasets, formal evaluation, comprehensive comparison). [DOCUMENTED ONLY — venue recommendation based on existing citation]

2. **IEEE Access** — open-access, broader scope, may accept systems papers with less algorithmic novelty. More feasible than TLT for current evidence. [DOCUMENTED ONLY — venue recommendation]

**Not recommended:** Top-tier ML/CV venues (NeurIPS, CVPR, ICCV, ICML) — VISTA uses existing models without algorithmic novelty and has pilot-scale evaluation. [VERIFIED — off-the-shelf model usage, 20 students]

---

## 10. What Would a Skeptical IEEE Reviewer Criticize First?

### Criticism 1: "Where is the open-set evaluation?"
A skeptical reviewer would immediately note that the 5.45% FAR is measured only among enrolled students, not against unknown impostors. Without open-set testing, the security claims are unsupported. [VERIFIED — `CLAIMS_TABLE.md` C-16, paper acknowledges in Section VIII]

### Criticism 2: "20 students is not a meaningful evaluation scale."
20 identities with 202 test crops is very small. Most face recognition papers evaluate on LFW (13K images, 5K pairs), IJB-C (10K subjects), or similar benchmarks. The pilot scale limits generalizability claims. [VERIFIED — paper acknowledges in Section VIII]

### Criticism 3: "The risk model performs below a trivial baseline."
XGBoost at 50% vs majority baseline at 53.5% means the ML model is worse than always predicting HIGH. A reviewer would ask why this is in the paper at all. The honest disclosure is appropriate, but the "Explainable Risk-Scoring" title framing becomes problematic. [VERIFIED — `risk_model_evaluation.json`]

### Criticism 4: "Where is the cascade ablation generator script?"
If a reviewer checks for reproducibility (standard in IEEE review), they would find that `cascade_ablation.json` has no generating script. The project's strongest result cannot be reproduced. [PARTIALLY VERIFIED — DC-4]

### Criticism 5: "What about demographic bias?"
No fairness evaluation was conducted. For a biometric system in education, this is a major ethical gap. A reviewer would flag this immediately. [VERIFIED — paper acknowledges in Section VIII]

### Criticism 6: "Where is the ethics approval?"
No IRB/ethics committee approval is documented. The consent form has placeholder fields. For biometric research, this is a publication blocker. [UNVERIFIED]

### Criticism 7: "The liveness formula in the paper doesn't match the code."
The paper references EAR in the liveness formula, but the code doesn't compute EAR. A careful reviewer checking the code would find this discrepancy. [CONTRADICTED — D-3]

### Criticism 8: "How is this different from using InsightFace off-the-shelf?"
The vision pipeline uses standard InsightFace (SCRFD + ArcFace) with a ResNet-50 fallback. A reviewer would ask what is novel beyond off-the-shelf usage. The answer: the cascade architecture (moderate novelty) and the system integration (engineering). [VERIFIED — off-the-shelf usage]

---

## Publication Readiness Score (1-10)

| Dimension | Score | Justification | Evidence |
|----------|-------|---------------|---------|
| **Originality** | 4/10 | Two-stage cascade is a moderate architectural contribution; deterministic computation firewall is a practical pattern; everything else is standard usage. No new algorithm proposed. | [VERIFIED — off-the-shelf models, standard techniques] |
| **Technical contribution depth** | 5/10 | The cascade ablation is a real, controlled experiment. The system is fully implemented (120 routes, 27 tables). But the contribution is integration-level, not deep algorithmic innovation. | [VERIFIED — system implemented, ablation controlled] |
| **Experimental rigor** | 4/10 | Some experiments have strong evidence (risk model reproduced exactly, cascade math verified). But: generator missing, non-deterministic split, no hypothesis test, closed-set only, no fairness eval, no cross-validation, pilot scale. | [PARTIALLY VERIFIED — multiple reproducibility gaps] |
| **Literature review quality** | 4/10 | 9 citations in bibliography, all real and correctly attributed. But no comparison to specific integrated classroom systems; no discussion of related deployment papers; gaps in educational analytics literature. | [VERIFIED — citations are real; DOCUMENTED ONLY — coverage is thin] |
| **Reprocibility** | 3/10 | Risk model fully reproducible (exact match). But: cascade ablation generator missing, threshold sweep non-deterministic, generator script out of sync with CSV, PyTorch seed not set, group latency extrapolated. | [PARTIALLY VERIFIED — major gaps] |
| **Ethical compliance** | 2/10 | Consent form exists but has placeholders; no signed records; no IRB approval; consent form contradicts implementation (photos not deleted, no encryption); no fairness evaluation; no deletion API. | [UNVERIFIED — critical gaps] |
| **Manuscript completeness** | 6/10 | Paper draft is complete (10 sections, 4 tables, figures). Internally consistent with verified numbers. Honest about limitations. But contains factual errors (EAR in liveness) and framing tension (risk model below baseline under "Risk-Scoring" title). | [PARTIALLY VERIFIED — draft complete, errors present] |
| **Overall** | 4/10 | A working, honestly-documented pilot system with one strong result (cascade) but significant reproducibility, ethical, and scale gaps. Conference paper feasible with revisions; journal paper requires substantial additional work. | [DOCUMENTED ONLY — holistic assessment] |

---

## Minimum Viable Manuscript Outline

```
Title: VISTA: A Two-Stage Cascade Approach for On-Premise 
       Classroom Face Recognition with Integrated Risk Scoring
       (or keep current title if preferred)

1. Introduction
   - Problem: fragmented attendance + risk + advising
   - Contributions: (1) two-stage cascade, (2) system integration, 
     (3) deterministic computation firewall
   - Scope: pilot, 20 students, closed-set

2. Related Work
   - Face recognition in education (ArcFace, SCRFD — cite [5],[6])
   - Student risk prediction (XGBoost, SHAP — cite [7],[3])
   - LLM advising (cite [4])
   - INTEGRATED CLASSROOM SYSTEMS (ADD THIS — currently missing)

3. System Architecture
   - Four-tier: Presentation, Vision, Application, Persistence
   - 120 routes, 27 tables, 3-role RBAC
   - ASCII diagram (from Document 2)

4. Methods
   - 4.1 Two-stage cascade (formal definition, thresholds)
   - 4.2 CIE policy engine
   - 4.3 Risk engine (rule-based production + XGBoost+SHAP diagnostic)
   - 4.4 AI study coach (deterministic computation firewall)
   - FIX: Remove EAR from liveness formula

5. Experimental Setup
   - Hardware (i7-13700H CPU)
   - Datasets: face NPZ (20 classes), synthetic risk (1000 rows)
   - Evaluation protocols (clearly state N=107 vs N=202)

6. Results
   - 6.1 Cascade ablation (Table II — VERIFIED)
   - 6.2 Threshold sweep (Table I — note non-deterministic split)
   - 6.3 ResNet-50 accuracy (90.10% Split B)
   - 6.4 Latency (Table III — note "modeled" not "measured")
   - 6.5 Risk model (Table IV — honest below-baseline disclosure)
   - 6.6 Coach groundedness (10/10 — narrow scope)

7. Limitations
   - Closed-set only (no impostor testing)
   - 20 students pilot scale
   - No demographic fairness evaluation
   - Synthetic risk data (circular labels)
   - Heuristic liveness (not neural anti-spoofing)
   - Risk model below baseline
   - No cross-validation
   - Cascade ablation generator to be committed (if still missing)

8. Ethics and Privacy
   - MUST ADD: ethics approval documentation
   - MUST ADD: consent procedures
   - MUST FIX: consent form contradictions
   - DPDP Act alignment (with caveats)
   - PII stripping for LLM

9. Conclusion and Future Work
   - Open-set testing
   - Multi-institution evaluation
   - Real longitudinal risk data
   - Neural anti-spoofing
   - Demographic fairness

References: [1]-[9] (all VERIFIED in references.bib)
```

---

*End of Document 8 — IEEE Publication Assessment*
