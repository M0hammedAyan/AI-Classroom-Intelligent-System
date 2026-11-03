# VISTA Research Audit — Summary of Key Findings

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phases:** 5-8 (Research Questions, Final Audit Documents)
**Auditor:** Autonomous Research Agent
**Date:** Audit conducted from repository evidence (Phases 1-4) + source code verification

---

## What Was Found

VISTA is a fully implemented, integrated intelligent education system combining face-recognition attendance, academic risk scoring with SHAP explainability, and a fact-grounded AI study coach. The system has 120 API routes, 27 database tables, 3-role RBAC, and a React frontend. [VERIFIED — programmatically confirmed]

**Strongest finding:** A two-stage face recognition cascade (ArcFace cosine matching at τ=0.55, then ResNet-50 fallback at τ=0.60) reduces the false reject rate from 16.83% to 1.98% on 202 test crops across 20 enrolled students, without increasing the false accept rate (5.45% unchanged). This is the most defensible quantitative result. [VERIFIED — `cascade_ablation.json`, math confirmed]

**Honest negative result:** The XGBoost risk model achieves 50.0% accuracy (Macro F1=0.3286), below the 53.5% majority-class baseline, and completely fails on the LOW minority class (F1=0.000). The production system correctly uses a deterministic rule engine instead. [VERIFIED — reproduced exactly in Phase 4]

**Other verified results:** ResNet-50 test accuracy 90.10% (Split B), latency benchmarks (SCRFD+ArcFace 71.23ms, group photo 77-311ms modeled), coach groundedness 10/10 (narrow scope), CIE policy thresholds, data leakage prevention in training. [VERIFIED or PARTIALLY VERIFIED — see individual documents]

---

## What Is Verifiable

| Claim/Result | Verifiability | Source |
|-------------|--------------|--------|
| Cascade FRR 16.83% → 1.98% | [VERIFIED] artifact + math; [PARTIAL] generator missing | `cascade_ablation.json` |
| XGBoost 50.0%, F1 0.3286 | [VERIFIED] reproduced exactly | `risk_model_evaluation.json` |
| Majority baseline 53.5% | [VERIFIED] reproduced | class distribution |
| 120 routes, 27 tables, 3-role RBAC | [VERIFIED] programmatically | `audit-inspection.md` |
| ResNet-50 test acc 90.10% | [VERIFIED] | `results_npz_splitB.txt` |
| No PII sent to LLM | [VERIFIED] code | `coach_service.py` |
| Data leakage prevention | [VERIFIED] code | `train_from_npz.py` |
| Coach 10/10 groundedness | [PARTIALLY VERIFIED] narrow scope | `coach_groundedness.json` |
| Latency 77-311ms group scaling | [PARTIALLY VERIFIED] extrapolated | `latency_benchmark.json` |
| CIE policy thresholds | [VERIFIED] | `cie_policy.py` |
| 14-image pilot 100% | [PARTIALLY VERIFIED] no script, trivial | `AUDIT.md` |

---

## What Requires Human Input Before Publication Can Proceed

### Critical (Publication Blockers)

1. **Institutional ethics approval** — no IRB/ethics committee approval is documented. The consent form has placeholder fields. This blocks any submission involving biometric data. [UNVERIFIED]

2. **Signed consent forms** — no signed copies exist in the repository. All 20 students must provide informed consent. [UNVERIFIED]

3. **Consent form corrections** — the consent form contradicts implementation in 4 ways: claims photos are deleted (they're retained), claims encrypted database (SQLite is plaintext), claims 3-5 photos (actual 27-41), claims 12-week retention (indefinite). [CONTRADICTED]

4. **Correct institution name** — the repo uses "DSATM" and "Dr. Ambedkar Institute of Technology" with different email domains (`@dsatm.edu` vs `@dr-ait.org`). [CONTRADICTED]

5. **Author contributions** — no CRediT statement exists. Individual contributions must be documented. [UNVERIFIED]

### High Priority (Must Address)

6. **Cascade ablation generator** — the project's strongest result cannot be reproduced because the generating script is missing. [PARTIALLY VERIFIED]

7. **Remove outdated 0.957 F1** — multiple documents present this as current; actual is 0.3286. [OUTDATED]

8. **Fix paper liveness formula** — references EAR which the code does not compute. [CONTRADICTED]

9. **Fix "21 students"** — current dataset has 20. [CONTRADICTED]

10. **Open-set impostor testing** — FAR measures wrong-student matches, not unknown-identity rejection. [UNVERIFIED]

11. **Demographic fairness evaluation** — not conducted; critical for biometric systems. [UNVERIFIED]

---

## Top 5 Actions Needed Before IEEE Submission

| # | Action | Why | Effort | Impact |
|---|--------|-----|--------|--------|
| 1 | **Obtain institutional ethics approval and collect signed consent forms** | Publication blocker — no reputable venue accepts biometric research without documented approval and consent | External (human) | Critical |
| 2 | **Commit the cascade ablation generator script** | The project's strongest result (FRR 16.83%→1.98%) cannot be reproduced from code — this would be flagged by any reviewer checking reproducibility | Medium (write `evaluate_cascade.py`) | Critical |
| 3 | **Correct all documentation contradictions** — remove outdated 0.957 F1, fix liveness EAR formula, fix "21 students," fix consent form claims | These are factual errors that a careful reviewer would immediately flag, undermining credibility | Low | High |
| 4 | **Add open-set impostor testing OR clearly document as a limitation** | Without this, security claims are unsupported; the 5.45% FAR only measures wrong-student matches among enrolled students, not unknown-identity rejection | Medium (create impostor set) or Low (document) | High |
| 5 | **Frame the paper honestly as a practical systems paper** — lead with cascade ablation, honestly disclose risk model below baseline, narrow the coach claim, state all limitations explicitly | Misframing (e.g., claiming algorithmic novelty or superior ML performance) would invite immediate rejection | Low (editing) | High |

---

## Document Index

| Document | Title |
|----------|-------|
| 01 | Research Identity |
| 02 | Technical Architecture |
| 03 | Dataset Audit |
| 04 | Experimental Results |
| 05 | Claim Verification |
| 06 | Literature Review |
| 07 | Ethics and Limitations |
| 08 | IEEE Publication Assessment |
| 09 | Questions Requiring Human Input |
| 10 | Final Research Dossier |

All documents are in: `d:\CipherTECH\Projects\AI-Classroom-Intelligent-System\VISTA_RESEARCH_AUDIT\`

---

*End of Audit Summary*
