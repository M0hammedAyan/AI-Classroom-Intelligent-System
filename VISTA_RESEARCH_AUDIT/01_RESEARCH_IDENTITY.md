# Document 1 — Research Identity

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 5 (Research Identity)
**Basis:** Repository evidence from `audit-inventory.md`, `audit-inspection.md`, `audit-claim-verification.md`, and direct source code inspection.

---

## 1. What Exactly Is VISTA?

VISTA is an integrated, on-premise academic intelligence platform that connects three functional subsystems into a single web application: (1) face-recognition-based classroom attendance, (2) academic risk scoring with explainability, and (3) a conversational AI study coach. [VERIFIED — `vista/vision/` (face pipeline), `vista/ml/` (risk engine), `vista/backend/app/services/coach_service.py` (AI coach), all present and implemented]

The system is structured as a FastAPI backend (120 REST endpoints, 27 database tables) with a React single-page frontend offering three role-scoped portals (Admin, Teacher, Student). [VERIFIED — `vista/backend/app/main.py` (120 routes), `vista/docs/DB_SCHEMA.md` + programmatic table count (27 tables), `audit-inspection.md` confirms 3-role RBAC]

### What Problem Does It Solve?

VISTA targets the operational disconnect between passive attendance tracking and timely academic advising. In traditional settings, attendance records remain isolated from continuous assessment marks and predictive analytics until semester examinations conclude, meaning faculty identify at-risk students reactively. [DOCUMENTED ONLY — stated as motivation in `paper/PAPER.md` Section I; this is the stated problem framing, not an empirically validated gap]

The system addresses three stated limitations of existing approaches:
1. **Fragmented pipeline execution** — vision attendance prototypes rarely integrate with functional LMS systems. [DOCUMENTED ONLY — paper framing, `PAPER.md` Section I]
2. **Opaque risk diagnostics** — ML risk models deployed as black boxes that instructors cannot interpret. [DOCUMENTED ONLY — paper framing, `PAPER.md` Section I]
3. **Unconstrained conversational advising** — LLM chatbots prone to numerical hallucination when advising students. [DOCUMENTED ONLY — paper framing, `PAPER.md` Section I]

### Who Are the Users?

Three user roles, enforced via JWT-based RBAC: [VERIFIED — `vista/backend/app/routes/auth.py`, `vista/backend/app/permissions.py`]

- **Admin** — school/department/class/subject management, student provisioning, face biometric enrollment, institutional audit monitoring, bulk risk recompute, export.
- **Teacher** — attendance marking (single-face and group-photo batch), CIE score entry, manual override with justification logging, subject-scoped data access only.
- **Student** — read-only own dashboard (attendance with provenance badges, CIE breakdowns, risk level), AI study coach chat.

The actual enrolled subjects are 20 real AI&ML department students at Dr. Ambedkar Institute of Technology (DSATM/DATM), Bengaluru. [VERIFIED — 20 USN-named directories in `dataset/`, team affiliations in `paper/PAPER.md`]

### Limitations in Existing Systems Addressed

Per the paper and source evidence: [DOCUMENTED ONLY — these are stated motivations, not empirically compared against specific deployed systems]

- Manual roll calls consuming lecture time and introducing clerical errors.
- Proxy-prone RFID badges and bottlenecked biometric kiosks.
- Attendance registries isolated from assessment analytics.
- Black-box ML risk models lacking explainability.
- LLM chatbots hallucinating academic facts without grounding.

**Honest assessment:** These are reasonable, widely-cited limitations. However, the repository contains no comparative evaluation against any specific deployed system, so the "existing systems" comparison remains a literature-level argument rather than an empirical one. [UNVERIFIED — no benchmarking against specific competing systems in the repo]

---

## 2. Central Research Question and Measurable Objectives

### Stated Research Question (inferred from paper structure)

*Can a two-stage face-recognition cascade (ArcFace cosine matching + ResNet-50 fallback), combined with a deterministic rule-based risk engine and a fact-grounded LLM study coach, reduce false rejection rates in classroom attendance while providing explainable, on-premise academic risk scoring?*

[DOCUMENTED ONLY — the paper does not state a single explicit research question; this is synthesized from the paper's contributions in `PAPER.md` Section I]

### Measurable Objectives (from paper contributions and evaluation artifacts)

| # | Objective | Metric | Evidence |
|---|-----------|--------|---------|
| O1 | Reduce false reject rate via cascade fallback | FRR: 16.83% → 1.98% on N=202 test crops | [VERIFIED — `evaluation/results/cascade_ablation.json`] |
| O2 | Maintain false accept rate through cascade | FAR unchanged at 5.45% | [VERIFIED — `cascade_ablation.json`] |
| O3 | Achieve sub-second multi-face latency on CPU | 77ms (1 face) to 311ms (45 faces) | [PARTIALLY VERIFIED — `latency_benchmark.json`; group scaling is analytically extrapolated, not directly timed per face count. `audit-claim-verification.md` DC-7] |
| O4 | Deploy auditable RBAC + CIE policy engine | 120 endpoints, 27 tables, 3-role RBAC, CIE best-2-of-3 rule | [VERIFIED — `audit-inspection.md` confirms programmatically] |
| O5 | Achieve zero-hallucination LLM coaching | 10/10 grounded queries, 0 hallucinations | [PARTIALLY VERIFIED — `coach_groundedness.json`; only 10 queries on 1 student, narrow scope] |
| O6 | Evaluate XGBoost risk model on synthetic data | Accuracy 50%, Macro F1 0.3286 (below 53.5% majority baseline) | [VERIFIED — `risk_model_evaluation.json`, reproduced exactly in Phase 4] |

---

## 3. Actual Research Contribution

### Honest Distinction: Research Novelty vs. Engineering Integration

**Engineering integration (dominant):**
VISTA is primarily a systems-integration project. It combines existing, well-established, open-source components — InsightFace (SCRFD + ArcFace), ResNet-50, XGBoost, SHAP, FastAPI, React — into a working classroom platform. The individual algorithms are not novel; they are pretrained models used as-is or fine-tuned on a small in-house dataset. [VERIFIED — `vista/vision/detect.py` wraps InsightFace `buffalo_l`, `vista/ml/model.pkl` is standard XGBoost, `vista/vision/personal_classifier.py` uses ImageNet-pretrained ResNet-50]

**Research novelty (genuine, but narrow):**

1. **Two-stage cascade for classroom attendance (strongest novelty claim):** The architecture of using ArcFace cosine matching as a first-stage filter with a personally-trained ResNet-50 classifier as a second-stage fallback to recover marginal cosine rejections is a specific, measurable architectural contribution. The ablation (FRR 16.83% → 1.98% without FAR increase) provides quantitative evidence for this design choice. [VERIFIED — `vista/vision/recognize.py` implements the cascade; `cascade_ablation.json` provides the ablation evidence] **However:** the generating script for the ablation is missing from the repo, so the result is not reproducible from code. [PARTIALLY VERIFIED — `audit-claim-verification.md` DC-4]

2. **Deterministic computation firewall for LLM coaching:** The architectural pattern of pre-computing all arithmetic facts in deterministic Python code before injecting only numerical aggregates (no PII) into the LLM system prompt is a legitimate design pattern. [VERIFIED — `coach_service.py:_call_openrouter()` injects only `facts` dict with "NO PII" label; `get_coach_facts()` extracts all numbers from DB before LLM call] This is more of an engineering pattern than a fundamental research contribution, but it is defensible as a practical contribution to educational AI.

3. **CIE policy engine as a formalized domain component:** The VTU CIE eligibility logic (best-2-of-3, absent≠0, eligibility threshold) is a domain-specific formalization. [VERIFIED — `vista/backend/app/cie_policy.py`] This is engineering, not research.

**Not research novelty:**
- Using XGBoost for risk prediction is standard practice in EDM. [The paper itself acknowledges this — `PAPER.md` Section II-B]
- Using SHAP for explainability is standard practice. [The paper acknowledges this — `PAPER.md` Section II-B]
- Using SCRFD + ArcFace is standard practice in face recognition. [The paper acknowledges this — `PAPER.md` Section II-A]
- The risk model performs below majority-class baseline (50% < 53.5%), so it is not a positive ML result. [VERIFIED — `risk_model_evaluation.json`]

---

## 4. Primary Classification

VISTA is best classified as an **integrated intelligent education system** with a small-scale empirical evaluation — not pure ML research, and not pure software engineering.

- It is **not pure ML research** because no new algorithm is proposed; all ML components use existing models (ArcFace, ResNet-50, XGBoost) with standard training procedures.
- It is **not pure software engineering** because it includes empirical evaluation (cascade ablation, threshold sweep, risk model evaluation, latency benchmarks, coach groundedness) and poses research questions about cascade design trade-offs.
- It **is an integrated system** because its value proposition is the coupling of vision + risk + coaching + policy into a single auditable platform.

[VERIFIED — this classification is supported by the full repository structure: `vista/vision/`, `vista/ml/`, `vista/backend/`, `vista/frontend/` all present and implemented]

---

## 5. Components Genuinely Contributing to Research Novelty

| Component | Novelty Level | Justification |
|-----------|--------------|---------------|
| Two-stage cascade (ArcFace + ResNet-50 fallback) | **Moderate** | Specific architectural choice with ablation evidence. Missing generator script weakens reproducibility. [PARTIALLY VERIFIED] |
| Deterministic computation firewall (LLM coach) | **Low-Moderate** | Practical design pattern; novel in educational context but not fundamentally new in LLM grounding literature (RAG-like). [VERIFIED implementation] |
| CIE policy engine | **Low** | Domain-specific engineering; useful but not a research contribution. [VERIFIED implementation] |
| SCRFD + ArcFace detection/embedding | **None** | Standard InsightFace usage. [VERIFIED — off-the-shelf] |
| ResNet-50 fine-tuning | **None** | Standard transfer learning. [VERIFIED] |
| XGBoost risk model | **None** | Standard algorithm, below-baseline performance. [VERIFIED] |
| SHAP explainability | **None** | Standard technique. [VERIFIED] |
| FastAPI + React platform | **None** | Standard web framework usage. [VERIFIED] |

---

## 6. Strongest Defensible Research Title

The current paper title is:

> *"VISTA: An Integrated On-Premise Vision and Explainable Risk-Scoring Platform for Classroom Academics"*

**Assessment:** This title is accurate and defensible. [VERIFIED — `paper/PAPER.md` title matches the actual system] The word "Platform" correctly signals that this is a systems/integration paper, not an algorithms paper. "Explainable Risk-Scoring" correctly reflects the SHAP diagnostic path (though the production risk engine is deterministic, not ML-based). "On-Premise" correctly reflects the CPU-only, no-cloud-inference design.

**Recommended alternative** (if the team wants to foreground the strongest contribution):

> *"VISTA: A Two-Stage Cascade Approach for On-Premise Classroom Face Recognition with Integrated Explainable Risk Scoring"*

This foregrounds the cascade ablation — the single strongest quantitative result — while remaining honest about the integration nature. [DOCUMENTED ONLY — recommendation, not verified claim]

---

## 7. Draft Abstract (Verified Evidence Only)

VISTA is an integrated on-premise academic intelligence platform connecting edge-assisted facial attendance, academic risk scoring, and grounded conversational advising. The system couples a CPU-optimized vision pipeline — combining SCRFD face detection with ArcFace 512-dimensional embeddings and a fine-tuned ResNet-50 fallback classifier — with a deterministic Continuous Internal Evaluation (CIE) policy engine and an XGBoost-plus-SHAP risk diagnostic framework. A two-stage recognition cascade (ArcFace cosine matching at threshold 0.55, followed by ResNet-50 classification at threshold 0.60) was evaluated on 202 unaugmented test crops across 20 enrolled student identities, achieving 92.57% accuracy (95% Wilson CI: [88.11, 95.45]) and reducing the false reject rate from 16.83% (cosine-only) to 1.98% (cascade) without increasing the false accept rate (5.45% in both conditions). [VERIFIED — `cascade_ablation.json`] End-to-end multi-face latency, modeled from component benchmarks on an Intel Core i7-13700H CPU, scales from 77 ms (1 face) to 311 ms (45 faces). [PARTIALLY VERIFIED — group scaling is analytically extrapolated, `audit-claim-verification.md` DC-7] The XGBoost risk model, trained on 1,000 synthetic student records, achieved 50.0% accuracy (Macro F1 = 0.3286), below the 53.5% majority-class baseline; the production system therefore uses a deterministic rule-based engine for all binding risk decisions, reserving the ML model for exploratory SHAP diagnostics. [VERIFIED — `risk_model_evaluation.json`, reproduced exactly in Phase 4] An AI study coach employing a deterministic computation firewall (all arithmetic pre-computed in Python, no PII sent to the LLM) achieved 100% factual grounding across 10 test queries with zero hallucinations. [PARTIALLY VERIFIED — `coach_groundedness.json`; narrow scope of 10 queries on 1 student] The evaluation is closed-set (no impostor testing) and pilot-scale (20 students), which are acknowledged limitations.

**Numbers omitted from this abstract that appear in some project documents but are NOT verified or are outdated:**
- "100% on 14-image pilot" — [PARTIALLY VERIFIED, statistically trivial, no reproducible script — `audit-claim-verification.md` Claim 1]
- "XGBoost F1 = 0.957" — [OUTDATED, from a historical 200-row balanced dataset that no longer exists — `audit-claim-verification.md` Claim 4]
- "Live classroom 7/7 students" — [DOCUMENTED ONLY, single snapshot, no saved per-image results]

---

## 8. Concise Problem Statement

Manual and proxy-prone attendance systems, standalone risk analytics that identify academic failure only after semester examinations, and ungrounded LLM advising tools operate as disconnected silos in educational institutions. This fragmentation delays timely pedagogical intervention. VISTA addresses this by integrating on-premise face-recognition attendance, a deterministic risk engine with SHAP explainability, and a fact-grounded AI study coach into a single auditable platform with role-based access control.

[DOCUMENTED ONLY — problem statement is the paper's framing; no empirical gap analysis against specific deployed systems is present in the repo]

---

## 9. Research Hypothesis

A two-stage recognition cascade — using ArcFace cosine similarity (τ = 0.55) as the primary matcher and a fine-tuned ResNet-50 classifier (τ = 0.60) as a fallback for marginal cosine rejections — will significantly reduce the false reject rate compared to cosine-only matching, without increasing the false accept rate, on a closed-set evaluation of 20 enrolled student identities.

[VERIFIED — this hypothesis is directly tested by the cascade ablation; result supports it: FRR 16.83% → 1.98%, FAR unchanged 5.45%. `cascade_ablation.json`. However, no formal hypothesis test (e.g., McNemar's test) is performed; only Wilson confidence intervals are provided. PARTIALLY VERIFIED for statistical rigor]

---

## 10. Measurable Research Objectives

| ID | Objective | Success Criterion | Status | Evidence |
|----|-----------|-------------------|--------|---------|
| RO1 | Reduce FRR via cascade fallback | FRR < 5% while FAR ≤ cosine-only | **Met** (FRR 1.98%) | [VERIFIED — `cascade_ablation.json`] |
| RO2 | Maintain FAR through cascade | FAR unchanged or reduced | **Met** (5.45% unchanged) | [VERIFIED — `cascade_ablation.json`] |
| RO3 | Sub-second multi-face latency on CPU | < 1000ms for ≤45 faces | **Met** (311ms at 45 faces, modeled) | [PARTIALLY VERIFIED — extrapolated, `DC-7`] |
| RO4 | Zero-hallucination LLM coaching | 0 hallucinations on test queries | **Met** (10/10, narrow scope) | [PARTIALLY VERIFIED — `coach_groundedness.json`] |
| RO5 | XGBoost risk model beats majority baseline | Accuracy > 53.5% | **Not met** (50.0%) | [VERIFIED — `risk_model_evaluation.json`] |
| RO6 | Open-set impostor rejection | FAR against unknown identities | **Not evaluated** | [UNVERIFIED — no impostor test set exists, `CLAIMS_TABLE.md` C-16] |
| RO7 | Bias/fairness evaluation | Demographic performance parity | **Not evaluated** | [UNVERIFIED — paper acknowledges this gap, `PAPER.md` Section VIII] |

---

*End of Document 1 — Research Identity*
