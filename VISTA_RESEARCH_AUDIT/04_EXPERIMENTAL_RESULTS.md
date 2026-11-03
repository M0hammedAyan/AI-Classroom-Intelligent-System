# Document 4 — Experimental Results

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 5 (Experimental Results)
**Basis:** `audit-inspection.md` (Experiment Audit section), `audit-claim-verification.md` (Claims 1-8 + A1-A8), direct inspection of `evaluation/results/*.json` and `training_results/*.txt`.

---

## 1. Experiment Inventory Table

| # | Experiment | Script | Dataset | Baseline | Proposed Method | Metrics | Results | Reproducibility | Status |
|---|-----------|--------|---------|----------|----------------|---------|---------|----------------|--------|
| E1 | ArcFace threshold sweep | `evaluation/evaluate_recognition.py` | NPZ (N=107) | N/A (threshold optimization) | Cosine matching across τ=0.30-0.80 | Acc, Prec, Recall, F1, FAR, FRR | Best F1=0.9246 at τ=0.30; production τ=0.55: Acc=78.50%, F1=0.8796 | Non-deterministic (`hash()` split) | [PARTIALLY VERIFIED] |
| E2 | Cascade ablation | **MISSING script** | NPZ (N=202) | Cosine-only (τ=0.55) | Full cascade (cosine + ResNet-50 @0.60) | Acc, Prec, Recall, F1, FAR, FRR + Wilson CIs | Cascade: Acc=92.57%, FRR=1.98% vs cosine: Acc=77.72%, FRR=16.83% | Generator absent; cascade logic verified in `recognize.py` | [PARTIALLY VERIFIED] |
| E3 | Latency benchmark | `evaluation/benchmark_latency.py` | Component timing | N/A | SCRFD+ArcFace, ResNet-50 CPU, cosine match, group scaling | Latency (ms), FPS | SCRFD+ArcFace=71.23ms; ResNet-50=32.5ms; 1 face=77ms, 45 faces=311ms | Single-run, no CIs; group scaling extrapolated | [PARTIALLY VERIFIED] |
| E4 | Risk model evaluation | `evaluation/evaluate_risk_model.py` | `student_data.csv` (N=200 test) | Majority-class (53.5%) | XGBoost + Logistic Regression | Acc, Macro F1, per-class P/R/F1, CM | XGBoost: Acc=50.0%, F1=0.3286 (below baseline); LR: Acc=36.5%, F1=0.3183 | Fully deterministic (rs=42); reproduced exactly | [VERIFIED] |
| E5 | Coach groundedness | `evaluation/evaluate_coach_groundedness.py` | Live DB (1 student) | N/A | 10 factual queries vs known answers | Pass/fail, hallucination count | 10/10 grounded, 0 hallucinations | Requires live LLM API; narrow scope | [PARTIALLY VERIFIED] |
| E6 | ResNet-50 training (Split A) | `train_from_npz.py` | NPZ (80/10/10) | N/A | ResNet-50 fine-tuning | Val acc, test acc, per-class | Test acc=86.76%, val acc=88.06%, best epoch 1 | sklearn rs=42; PyTorch seed not set | [PARTIALLY VERIFIED] |
| E7 | ResNet-50 training (Split B) | `train_from_npz.py` | NPZ (70/15/15) | N/A | ResNet-50 fine-tuning | Val acc, test acc, per-class | Test acc=90.10%, val acc=93.07%, best epoch 1 | sklearn rs=42; PyTorch seed not set | [PARTIALLY VERIFIED] |
| E8 | 14-image pilot | **MISSING script** | 14 images (2 students) | N/A | Manual recognition | Pass/fail | 100% (14/14) | No script, no saved results | [PARTIALLY VERIFIED] |
| E9 | Live classroom pilot | **MISSING script** | 7-student group photo | N/A | Full cascade | All correct? | 7/7 marked present | Single snapshot, no saved results | [DOCUMENTED ONLY] |
| E10 | Rule engine UCI validation | `vista/ml/validate_uci.py` | UCI Student Performance (external) | N/A | Rule engine sanity check | Recall/precision vs G3 | Not documented in eval/results/ | External dataset not in repo | [DOCUMENTED ONLY] |

---

## 2. Per-Experiment Full Analysis

### Experiment E1: ArcFace Threshold Sweep

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Script | `evaluation/evaluate_recognition.py` | [VERIFIED] |
| Dataset | `facial_pipeline_results.npz`, 107 test samples, 20 classes | [VERIFIED — `recognition_threshold_sweep.json`] |
| Method | Cosine similarity against per-class mean gallery prototypes | [VERIFIED — script logic matches] |
| Split | 70/15/15 using `hash(src) % 100` | [PARTIALLY VERIFIED — non-deterministic] |
| Metrics | Accuracy, Precision, Recall, Macro F1, FAR, FRR across 11 thresholds (0.30-0.80) | [VERIFIED] |
| Results | Optimal τ=0.30 (F1=0.9246, FAR=11.21%); Production τ=0.55 (Acc=78.50%, F1=0.8796, FAR=7.48%, FRR=14.02%) | [VERIFIED in saved JSON, but fresh run differs] |

**Critical reproducibility issue:** The split uses `hash(src) % 100` which is non-deterministic across Python processes. A fresh run produced N=111 (vs saved N=107), acc=0.7748 (vs 0.785), F1=0.8731 (vs 0.8796). The methodology is sound but the exact figures are not stable. [VERIFIED — `audit-claim-verification.md` DC-5]

**Assessment:** The threshold sweep correctly identifies the precision-recall trade-off and justifies τ=0.55 as a production operating point (high precision 91.30%, moderate FAR 7.48%). However, the non-deterministic split means results are not bit-reproducible. [PARTIALLY VERIFIED]

### Experiment E2: Cascade Ablation

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Script | **MISSING** — only `paper/figures/plot_results.py` reads the JSON | [PARTIALLY VERIFIED — `audit-claim-verification.md` DC-4] |
| Dataset | NPZ, 202 test samples, 20 gallery classes (30% holdout of unaugmented) | [VERIFIED — `cascade_ablation.json`] |
| Baseline | Cosine-only matching at τ=0.55 | [VERIFIED] |
| Proposed | Full cascade: cosine (τ=0.55) + ResNet-50 fallback (τ=0.60) | [VERIFIED — cascade logic in `recognize.py`] |
| Results | Cosine: Acc=77.72%, FRR=16.83%, FAR=5.45%. Cascade: Acc=92.57%, FRR=1.98%, FAR=5.45% (unchanged). FRR improvement: −14.85pp | [VERIFIED — arithmetic confirmed: TP=157→187, FN=34→4, FP=11→11] |

**Key finding (VERIFIED):** The cascade recovers 30 false rejects (34→4) without adding false accepts (11→11). This is the strongest single result in the project.

**Caveats:**
1. Generator script is missing — the 202-crop ablation cannot be regenerated from code. [PARTIALLY VERIFIED]
2. The ablation uses NPZ mean-prototype galleries, not the production DB-gallery path. It is a faithful simulation, not a production code path run. [DOCUMENTED ONLY]
3. Closed-set only — all 202 crops belong to the 20 enrolled identities. FAR measures wrong-student matches, not unknown-impostor accepts. [VERIFIED]
4. No formal hypothesis test — only Wilson CIs are provided. [VERIFIED]

**Reproducibility:** Cascade logic verified in source; measurement artifact present and internally consistent; generator absent. Cannot reproduce the exact split. [PARTIALLY VERIFIED]

### Experiment E3: Latency Benchmark

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Script | `evaluation/benchmark_latency.py` | [VERIFIED] |
| Hardware | Intel Core i7-13700H (16 logical / 10 physical cores), 1243 MB RAM RSS | [VERIFIED — `latency_benchmark.json`] |
| Component results | SCRFD+ArcFace: 71.23ms avg; ResNet-50 CPU: 32.5ms (30.8 FPS); Cosine match (100 gallery): 1.07ms | [VERIFIED] |
| Group photo scaling | 1 face=77ms, 45 faces=311ms (fast path); 1 face=109ms, 45 faces=422ms (hybrid path) | [PARTIALLY VERIFIED] |

**Critical caveat:** The group photo scaling values are computed via **analytical linear extrapolation** (`fast_path_ms = base_det_time + face_count * (5.0 + per_face_match_time)`), not by directly timing group photos of N faces. [PARTIALLY VERIFIED — `audit-claim-verification.md` DC-7, A3]

**Assessment:** Component-level timings (SCRFD, ArcFace, ResNet-50, cosine match) are real measurements. Group photo scaling is modeled from these components. Single-run with no confidence intervals or variance. [PARTIALLY VERIFIED]

### Experiment E4: Risk Model Evaluation

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Script | `evaluation/evaluate_risk_model.py` | [VERIFIED] |
| Dataset | `student_data.csv` (synthetic, 1000 rows, test=200) | [VERIFIED] |
| Split | Stratified 80/20, random_state=42 | [VERIFIED — deterministic] |
| Baseline | Majority-class (predict HIGH for all) = 53.5% | [VERIFIED] |
| Models | XGBoost (n_estimators=100, max_depth=4, lr=0.1); Logistic Regression (max_iter=1000, balanced) | [VERIFIED] |
| XGBoost results | Acc=50.0%, Macro F1=0.3286, LOW F1=0.000, MEDIUM F1=0.3893, HIGH F1=0.5966 | [VERIFIED — reproduced exactly] |
| LR results | Acc=36.5%, Macro F1=0.3183 | [VERIFIED] |
| Majority baseline | 53.5% | [VERIFIED — 107/200] |

**Key finding (VERIFIED):** XGBoost (50.0%) performs **below** the majority-class baseline (53.5%). The model completely fails on the LOW minority class (0/12 correct, F1=0.000). This is honestly disclosed in the paper.

**Reproducibility (VERIFIED):** The evaluation is fully deterministic (`random_state=42`, stratified split). Phase 4 reproduced the result byte-for-byte: acc=0.5, macro_f1=0.3286, confusion matrix `[[0,3,9],[1,29,51],[0,36,71]]`.

**Confusion matrix:**
```
              Predicted
              LOW  MED  HIGH
Actual LOW  [  0    3     9  ]   (12)
Actual MED  [  1   29    51  ]   (81)
Actual HIGH [  0   36    71  ]   (107)
```
[VERIFIED — matches artifact and reproduction]

**Root cause:** No class weighting in XGBoost → model optimizes for majority class (HIGH) at the expense of minority class (LOW). The production system correctly uses the deterministic rule engine, not XGBoost, for actual risk decisions. [VERIFIED — `vista/backend/app/routes/risk.py` confirms rule engine is production path]

### Experiment E5: Coach Groundedness

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Script | `evaluation/evaluate_coach_groundedness.py` | [VERIFIED] |
| Dataset | Live DB for student `1DA24AI403` | [VERIFIED] |
| Provider | OpenRouter, model `nvidia/nemotron-3.5-super-vl:free` | [VERIFIED — `coach_groundedness.json`] |
| Method | 10 factual queries with pre-known correct answers; manual pass/fail | [VERIFIED] |
| Results | 10/10 grounded, 0 hallucinations, 100% groundedness | [VERIFIED-per-artifact] |

**Limitations:**
1. Only 10 queries — very small sample. [VERIFIED]
2. Only 1 student tested (`1DA24AI403`). [VERIFIED]
3. No adversarial prompt injection testing. [VERIFIED — acknowledged in artifact]
4. Requires live OpenRouter API key — not independently re-runnable without external service. [VERIFIED]
5. Results not generalizable to all possible student queries. [VERIFIED]

**Assessment:** The 10/10 result is a promising indicator of the deterministic computation firewall's effectiveness, but the evaluation scope is too narrow to support strong generalization claims. [PARTIALLY VERIFIED]

### Experiments E6 & E7: ResNet-50 Training (Splits A and B)

| Attribute | Split A | Split B | Evidence |
|-----------|---------|---------|---------|
| Script | `train_from_npz.py` | `train_from_npz.py` | [VERIFIED] |
| Split ratio | 80/10/10 | 70/15/15 | [VERIFIED] |
| Train samples | 16,080 (augmented) | 14,070 (augmented) | [VERIFIED — `results_npz_splitA.txt`, `results_npz_splitB.txt`] |
| Val samples | 67 (unaugmented) | 101 (unaugmented) | [VERIFIED] |
| Test samples | 68 (unaugmented) | 101 (unaugmented) | [VERIFIED] |
| Epochs run | 8 (early stop patience=7) | 8 (early stop patience=7) | [VERIFIED] |
| Best epoch | 1 | 1 | [VERIFIED] |
| Best val accuracy | 88.06% | 93.07% | [VERIFIED] |
| Test accuracy | 86.76% | **90.10%** | [VERIFIED — Split B is production model] |
| Train/test gap | 9.78% | 6.40% | [VERIFIED] |

**Key observations:**
1. Best epoch is 1 in both splits — the model learns most from the first epoch, suggesting the ImageNet-pretrained backbone is already strong and fine-tuning provides marginal gains. [VERIFIED]
2. Split B (90.10%) is the production model loaded by `personal_classifier.py`. [VERIFIED]
3. Per-class weaknesses: `1DA22AI402` (0/5 correct, F1=0.000 in Split B) and `1DA24AI403` (3/5, F1=0.4615 in Split B) consistently underperform. [VERIFIED]
4. PyTorch seed not explicitly set — minor nondeterminism risk. [PARTIALLY VERIFIED]

**Reproducibility:** Training script present; sklearn `random_state=42` set for splits; PyTorch seed not explicitly set. Training not re-attempted in Phase 4 (heavy CPU). [PARTIALLY VERIFIED]

### Experiment E8: 14-Image Pilot

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Script | **MISSING** | [PARTIALLY VERIFIED] |
| Dataset | 14 images of 2 students (1DA23AI042, 1DA23AI050) | [VERIFIED — `AUDIT.md`] |
| Method | Manual recognition | [DOCUMENTED ONLY] |
| Results | 100% (14/14) | [PARTIALLY VERIFIED — no per-image results saved] |

**Assessment:** This is a trivial 2-class/14-image feasibility check, not a statistically meaningful evaluation. No evaluation script exists. No saved per-image results. No confidence intervals. It must not be presented as a recognition accuracy figure alongside the 202-crop or 90.10% results. [PARTIALLY VERIFIED — `audit-claim-verification.md` Claim 1]

### Experiment E9: Live Classroom Pilot

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Date | October 30, 2026 | [DOCUMENTED ONLY — `PAPER.md` Section V-B] |
| Session | Deep Learning `22AIU701` | [DOCUMENTED ONLY] |
| Subjects | 7 enrolled students in group photo | [DOCUMENTED ONLY] |
| Results | 7/7 marked present, confidence 58%-96% | [DOCUMENTED ONLY — single snapshot, no saved results] |

**Assessment:** A single in-situ snapshot with no saved per-image results, no ground-truth verification script, and no statistical analysis. [DOCUMENTED ONLY]

### Experiment E10: Rule Engine UCI Validation

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Script | `vista/ml/validate_uci.py` | [VERIFIED — script present] |
| Dataset | UCI Student Performance (external, Portuguese secondary school) | [DOCUMENTED ONLY — not in repo] |
| Purpose | Sanity-check rule engine against known G3 outcomes | [VERIFIED] |
| Results | Not saved in `evaluation/results/` | [UNVERIFIED — no result artifact] |

**Assessment:** The validation script exists but no results are saved. The UCI dataset is not in the repository. This is a sanity check, not a formal evaluation. [DOCUMENTED ONLY]

---

## 3. Face Recognition Experiments: Cosine-Only vs. Two-Stage Cascade (Detailed)

### Comparison Table (VERIFIED from `cascade_ablation.json`)

| Metric | Cosine Only (τ=0.55) | Two-Stage Cascade | Improvement | Evidence |
|--------|----------------------|-------------------|-------------|---------|
| True Positives (TP) | 157 | 187 | +30 | [VERIFIED] |
| False Positives (FP) | 11 | 11 | 0 | [VERIFIED] |
| False Negatives (FN) | 34 | 4 | −30 | [VERIFIED] |
| Accuracy | 77.72% [71.50, 82.91] | 92.57% [88.11, 95.45] | +14.85pp | [VERIFIED] |
| Precision | 93.45% [88.66, 96.30] | 94.44% [90.33, 96.87] | +0.99pp | [VERIFIED] |
| Recall | 82.20% [76.16, 86.97] | 97.91% [94.74, 99.18] | +15.71pp | [VERIFIED] |
| F1-Score | 0.8747 | 0.9614 | +0.0867 | [VERIFIED] |
| FAR | 5.45% [3.07, 9.49] | 5.45% [3.07, 9.49] | 0 | [VERIFIED] |
| FRR | 16.83% [12.30, 22.60] | 1.98% [0.77, 4.98] | −14.85pp | [VERIFIED] |

**Interpretation:** The ResNet-50 fallback recovers 30 of 34 cosine-rejected true probes (true students whose ArcFace embedding fell below the 0.55 threshold) by re-identifying them via the fine-tuned classifier. Crucially, this recovery does not introduce any new false accepts (FP remains 11). [VERIFIED]

**Statistical rigor:** Wilson 95% confidence intervals are provided for all metrics, appropriate for the N=202 sample size. However, no formal hypothesis test (e.g., McNemar's test for paired proportions) is performed to establish statistical significance. [PARTIALLY VERIFIED]

**Closed-set caveat:** All 202 test crops belong to the 20 enrolled identities. The 5.45% FAR measures wrong-student matches among the enrolled, NOT unknown-impostor acceptance. Open-set FAR is unmeasured. [VERIFIED — `CLAIMS_TABLE.md` C-16]

### Threshold Sweep Results (N=107)

| τ | Accuracy | Precision | Recall | F1 | FAR (%) | FRR (%) | Evidence |
|---|---------|-----------|--------|-----|---------|---------|---------|
| 0.30 | 85.98% | 88.46% | 96.84% | **0.9246** | 11.21% | 2.80% | [VERIFIED in JSON] |
| 0.55 (production) | 78.50% | 91.30% | 84.85% | 0.8796 | 7.48% | 14.02% | [VERIFIED in JSON] |
| 0.70 | 62.62% | 95.24% | 60.61% | 0.7407 | 2.80% | 34.58% | [VERIFIED in JSON] |

**Rationale for τ=0.55:** While τ=0.30 maximizes F1 (0.9246), it yields unacceptable FAR (11.21%). τ=0.55 provides high precision (91.30%) with moderate FAR (7.48%), delegating marginal rejections to the ResNet-50 fallback. [VERIFIED — paper logic is sound]

---

## 4. Academic Risk Prediction: XGBoost vs. Majority-Class Baseline (Detailed)

### Consolidated Results Table (VERIFIED)

| Model | Accuracy | Macro F1 | LOW F1 | MED F1 | HIGH F1 | Evidence |
|-------|---------|----------|--------|--------|---------|---------|
| XGBoost | 50.00% [43.14, 56.86] | 0.3286 | 0.0000 | 0.3893 | 0.5966 | [VERIFIED — reproduced] |
| Logistic Regression | 36.50% | 0.3183 | — | — | — | [VERIFIED] |
| **Majority baseline** | **53.50%** [46.59, 60.28] | — | — | — | — | [VERIFIED — 107/200] |

**Result:** XGBoost (50.0%) < Majority baseline (53.5%). The model performs below the trivial baseline. [VERIFIED]

### Per-Class Performance (XGBoost, VERIFIED)

| Class | Precision | Recall | F1 | Support | Evidence |
|-------|-----------|--------|-----|---------|---------|
| LOW | 0.00% | 0.00% | 0.0000 | 12 | [VERIFIED — 0/12 correct] |
| MEDIUM | 42.65% | 35.80% | 0.3893 | 81 | [VERIFIED — 29/81 correct] |
| HIGH | 54.20% | 66.36% | 0.5966 | 107 | [VERIFIED — 71/107 correct] |
| Macro Avg | 32.28% | 34.05% | 0.3286 | 200 | [VERIFIED] |

### Confusion Matrix (VERIFIED — reproduced exactly)

```
              Predicted
              LOW  MED  HIGH
Actual LOW  [  0    3     9  ]   → 0% recall (all misclassified)
Actual MED  [  1   29    51  ]   → 35.8% recall (majority misclassified as HIGH)
Actual HIGH [  0   36    71  ]   → 66.4% recall (best, but still 36 misclassified)
```

**Root cause:** XGBoost does not use class weighting. With severe imbalance (6% LOW, 53.5% HIGH), the model optimizes for the majority class and completely ignores the minority. [VERIFIED — `train.py` config has no `scale_pos_weight` or sample weights]

**Production decision:** The production system uses the deterministic rule engine (`calculate_risk_from_metrics`), NOT XGBoost. XGBoost is auxiliary, used only for SHAP explainability via the `/risk/explain` endpoint. [VERIFIED — `risk.py` route confirms this]

---

## 5. Consolidated Results Table (Paper-Ready)

### Vision Results

| Experiment | N | Method | Accuracy | F1 | FAR | FRR | Classification |
|-----------|---|--------|----------|-----|-----|-----|---------------|
| Threshold sweep | 107 | Cosine (τ=0.55) | 78.50% | 0.8796 | 7.48% | 14.02% | [VERIFIED in JSON, non-reproducible split] |
| Cascade ablation | 202 | Cosine-only (τ=0.55) | 77.72% | 0.8747 | 5.45% | 16.83% | [VERIFIED, generator missing] |
| Cascade ablation | 202 | Cascade (cosine+ResNet) | **92.57%** | **0.9614** | 5.45% | **1.98%** | [VERIFIED, generator missing] |
| ResNet-50 (Split B) | 101 | Classifier standalone | 90.10% | — | — | — | [VERIFIED] |
| Latency | — | SCRFD+ArcFace | 71.23ms | — | — | — | [VERIFIED] |
| Latency | — | Group photo (45 faces) | 311ms | — | — | — | [PARTIALLY VERIFIED — extrapolated] |

### Risk Model Results

| Model | N | Accuracy | Macro F1 | Baseline | Classification |
|-------|---|---------|----------|---------|---------------|
| XGBoost | 200 | 50.00% | 0.3286 | 53.50% | [VERIFIED — reproduced, below baseline] |
| Logistic Regression | 200 | 36.50% | 0.3183 | 53.50% | [VERIFIED — below baseline] |

### Coach Results

| Experiment | N | Result | Classification |
|-----------|---|--------|---------------|
| Groundedness | 10 queries, 1 student | 10/10 grounded, 0 hallucinations | [PARTIALLY VERIFIED — narrow scope] |

---

## 6. Reproducibility Assessment Per Experiment

| Experiment | Determinism | Generator in Repo? | Reproduced? | Assessment | Evidence |
|-----------|------------|-------------------|-------------|------------|---------|
| E1 Threshold sweep | Non-deterministic (`hash()`) | Yes | No (fresh run differs) | **Not bit-reproducible** | [VERIFIED — `audit-claim-verification.md` DC-5] |
| E2 Cascade ablation | Unknown | **No** | Cannot attempt | **Not reproducible** (no code) | [VERIFIED — DC-4] |
| E3 Latency benchmark | Single-run, no CIs | Yes | Not attempted | Self-reported; group scaling extrapolated | [PARTIALLY VERIFIED] |
| E4 Risk model | Deterministic (rs=42) | Yes | **Yes — exact match** | **Reproducible** | [VERIFIED — Phase 4] |
| E5 Coach groundedness | Requires external LLM | Yes | Not attempted | Narrow scope; not generalizable | [PARTIALLY VERIFIED] |
| E6 ResNet-50 Split A | Mostly deterministic | Yes | Not attempted | Reproducible in principle; PyTorch seed not set | [PARTIALLY VERIFIED] |
| E7 ResNet-50 Split B | Mostly deterministic | Yes | Not attempted | Reproducible in principle; PyTorch seed not set | [PARTIALLY VERIFIED] |
| E8 14-image pilot | N/A | **No** | No | Not reproducible (manual) | [PARTIALLY VERIFIED] |
| E9 Live classroom | N/A | **No** | No | Single snapshot | [DOCUMENTED ONLY] |
| E10 UCI validation | N/A | Yes (script) | Not documented | External dataset not in repo | [DOCUMENTED ONLY] |

---

## 7. Gaps in Experimental Validation

| Gap | Impact | Evidence | Priority |
|-----|--------|---------|---------|
| Open-set / impostor testing absent | FAR does not measure unknown-identity rejection | [VERIFIED — `CLAIMS_TABLE.md` C-16] | **Critical** |
| Cascade ablation generator missing | Cannot reproduce the project's strongest result | [VERIFIED — `audit-claim-verification.md` DC-4] | **Critical** |
| No real longitudinal risk data | Risk model trained on synthetic, circular data | [VERIFIED] | **High** |
| Non-deterministic threshold sweep | Results not stable across process restarts | [VERIFIED — DC-5] | **High** |
| No formal hypothesis test for cascade | Statistical significance not established | [VERIFIED — only Wilson CIs] | **Medium** |
| No cross-validation for risk model | Single train/test split only | [VERIFIED] | **Medium** |
| No class weighting for XGBoost | Minority class (LOW) completely fails | [VERIFIED — F1=0.000] | **Medium** |
| No demographic bias/fairness evaluation | Cannot assess demographic performance parity | [VERIFIED — paper acknowledges gap] | **High** |
| No adversarial coach testing | Groundedness only tested on 10 benign queries | [VERIFIED] | **Medium** |
| No multi-institution evaluation | Single classroom, 20 students only | [VERIFIED] | **High** |
| Latency group scaling extrapolated | Not directly measured per face count | [VERIFIED — DC-7] | **Low** |
| PyTorch seed not set | Minor nondeterminism in ResNet-50 training | [PARTIALLY VERIFIED] | **Low** |

---

*End of Document 4 — Experimental Results*
