# VISTA Project — Phase 4 Critical Claim Verification Report

**Generated:** Phase 4 Research Audit (Critical Claim Verification)
**Auditor:** Autonomous Research Agent
**Repository root:** `d:\CipherTECH\Projects\AI-Classroom-Intelligent-System`
**Scope:** Independent verification of the 8 specific quantitative claims, plus additional claims found in documentation. Method: locate source → identify experiment → locate evaluation code → verify dataset → find raw artifacts/logs → attempt safe reproduction → assign evidence classification.

**Evidence classification key:**
- **VERIFIED** — claim matches a present, internally-consistent artifact AND (where attempted) reproduces.
- **PARTIALLY VERIFIED** — claim is documented consistently and/or matches an artifact, but supporting reproducible code/data is absent, trivial, or incomplete.
- **UNVERIFIED** — no supporting artifact or code could be located.
- **OUTDATED** — the figure was correct for an earlier experiment/dataset but no longer reflects the current state.
- **CONTRADICTED** — a present artifact/code shows a different value for the same experiment.

**Reproduction note:** Two claims were independently reproduced from the live environment using `.venv` (Python 3.11.9, pandas 3.1.0, scikit-learn 1.9.1, xgboost 3.2.0, numpy 2.4.6, torch 2.15.0 CPU, shap 0.51.0). Temporary probes were used, executed, then deleted; no production code, datasets, or research documents were modified. `git status` is clean after the run.

---

## Claim Verification Matrix

| # | Claim | Source (where stated) | Dataset | Evaluation Code | Evidence Found | Classification | Notes |
|---|-------|----------------------|---------|-----------------|----------------|----------------|-------|
| 1 | Face recognition 100% on 14 samples | `README.md` ("What VISTA Does"), `AUDIT.md` §3, `REPORT.md`, `NEEDS_YOUR_INPUT.md` | 14 images of 2 students (Saheel=1DA23AI042, Sujal=1DA23AI050) | None (no script computes 14/14; `train_splitB.py` is a 26-line shim, `personal_classifier.py:27` is just MODEL_PATH) | Manual feasibility note in `AUDIT.md`; no per-image results, no labeled test set, no log | **PARTIALLY VERIFIED** | Trivial 2-class/14-image pilot, honestly caveated as a feasibility check. Distinct from 202-crop and 90.10% evals. |
| 2 | Cosine-only accuracy 77.72% (FRR 16.83%) | `cascade_ablation.json`, `CLAIMS_TABLE.md` C-10, `paper/PAPER.md` | `facial_pipeline_results.npz`, 202 test crops, 20 gallery classes (30% holdout) | Generator script **MISSING** (only `plot_results.py` reads the JSON) | Artifact present; math internally consistent (TP=157, FP=11, FN=34) | **VERIFIED** (reproducibility PARTIAL) | FRR=34/202=0.1683, FAR=11/202=0.0545 confirmed. Closed-set. |
| 3 | Two-stage cascade accuracy 92.57% (FRR 1.98%) | `cascade_ablation.json`, `CLAIMS_TABLE.md` C-11, `paper/PAPER.md` | same 202 crops, 20 identities | Cascade logic **VERIFIED** in `recognize.py`; ablation generator **MISSING** | Artifact present; cascade impl present; math consistent (TP=187, FP=11, FN=4) | **VERIFIED** (reproducibility PARTIAL) | Recovers 30 false rejects (34→4), FAR unchanged (5.45%). Eval simulates cascade via NPZ prototypes, not the production DB-gallery path. |
| 4 | XGBoost accuracy 95.7% / F1=0.957 | `AUDIT.md` §6, `vista/ml/CLAUDE.md`, `vista/README.md`, `vista/PROJECT_REPORT.md`, `vista/PLANB.md`, `docs_backup_final/ROADMAP.md` | Earlier balanced ~200-row synthetic set (no longer in repo) | `vista/ml/train.py` (historical) | Documented as a historical 200-row balanced run; current eval gives 50% | **OUTDATED** | 0.957 = macro F1 on a balanced 200-row set that no longer exists; AUDIT.md explains the drop to 0.329 on scaling to 1000 rows. |
| 5 | XGBoost accuracy 50% (alternative) | `risk_model_evaluation.json`, `CLAIMS_TABLE.md` C-19, `paper/PAPER.md`, `EXHIBITION_KIT.md`, `VIVA_QA.md` | `student_data.csv` (synthetic, 1000 rows), 80/20 stratified (rs=42), test=200 | `evaluation/evaluate_risk_model.py` (retrains fresh XGB) | Artifact present; **REPRODUCED EXACTLY** (acc=0.5, F1=0.3286, CM=[[0,3,9],[1,29,51],[0,36,71]]) | **VERIFIED** | Below majority baseline (53.5%); honest. Current authoritative figure. |
| 6 | Majority-class baseline 53.5% | `CLAIMS_TABLE.md` C-20, `docs_backup_final/REPORT_ch7.md` | `student_data.csv`: full HIGH=535(53.5%)/MED=405/LOW=60; test HIGH=107(53.5%)/MED=81/LOW=12 | Derived from `risk_model_evaluation.json` supports | **REPRODUCED** (107/200=0.535); class counts confirmed | **VERIFIED** | Majority class is HIGH; 50% model < 53.5% baseline. |
| 7 | Synthetic academic dataset of 1,000 samples | `CLAIMS_TABLE.md` C-18, `AUDIT.md`, `generate_sample_data.py` | `vista/ml/data/student_data.csv` = 1000 rows | `generate_sample_data.py` present BUT out of sync | 1000 rows confirmed; synthetic generator present; script makes 200 rows w/ different label logic | **VERIFIED** (with reproducibility caveat) | Re-running committed script would overwrite the CSV with a non-matching 200-row file. S001 label contradicts current `_derive_label`. |
| 8 | 202 test crops & 20 enrolled identities | `cascade_ablation.json`, `CLAIMS_TABLE.md` C-10/C-11 | `facial_pipeline_results.npz` (real unaugmented face crops, 20 USN dirs) | Generator script **MISSING** | 202 & 20 confirmed in artifact; ~30% of ~671 unaugmented originals | **VERIFIED** (reproducibility PARTIAL) | Crops are real SCRFD detections from 20 enrolled students (closed-set); no impostor set. |

---

## Claim 1 Detail: Face recognition accuracy of 100% on 14 samples

**Source location:** The figure appears in five documents:
- `README.md` — "What VISTA Does" table: *"Vision | Identify students from classroom photos (InsightFace ArcFace / ResNet-50 classifier: 100% on 14-image 2-student pilot test set; 90.10% test accuracy on 20-class .npz split B)"*. This is the most carefully qualified form.
- `AUDIT.md` (Section 3, "Pilot Image & Live Group Verification Sets"): *"Initial Pilot Cohort: 14 images representing 2 students (Saheel and Sujal). Result: 100% correct match (14/14 faces matched to true student ID, zero false accepts, zero false rejects)."* with the explicit caveat *"This figure represents an initial feasibility check and must not be conflated with larger cohort benchmarks."*
- `REPORT.md`, `NEEDS_YOUR_INPUT.md`, `vista/docs/PITCH_DECK.md` (the latter was flagged "UNQUALIFIED" by `DOCS_SYNC_REPORT.md` and qualified to "100% on 14 photos of 2 students; 90.10% on 20-class .npz split B").

**The 14 samples:** Per `AUDIT.md`, they are 14 images of exactly 2 students — Saheel Pradhan (USN `1DA23AI042`) and Sujala Agrahari (USN `1DA23AI050`). This is a 2-class recognition problem with ~7 images per class.

**Evaluation code:** None found. The `DOCS_SYNC_REPORT.md` cross-references `vista/vision/personal_classifier.py:27` and `train_splitB.py:120` as the code basis, but:
- `train_splitB.py` is only 26 lines (a thin shim calling `train.py:main(splits=["B"])`) — there is no line 120; the reference is stale.
- `personal_classifier.py:27` is the `MODEL_PATH` constant, not a 14-sample evaluation.
No script in the repository computes a 14/14 recognition result. There is no saved per-image prediction file, no ground-truth label file for the 14 images, and no experiment log enumerating the 14 matches.

**Meaningfulness:** This is a **trivial small-set result**. A 100% match on 14 photos of 2 students is an expected feasibility sanity check, not a statistically meaningful recognition evaluation. There are no confidence intervals and no held-out impostor test. The claim is correctly caveated as an "initial feasibility check" in `AUDIT.md` and `README.md`, but was historically presented without qualification in `PITCH_DECK.md` (per `DOCS_SYNC_REPORT.md`).

**Relationship to the 202-crop evaluation:** Entirely **different**. The repo contains three distinct face test sets:
1. The 14-image / 2-student pilot (this claim) — manual feasibility.
2. The 107-sample threshold sweep (`recognition_threshold_sweep.json`, `evaluate_recognition.py`).
3. The 202-crop cascade ablation (`cascade_ablation.json`).
4. The 101-sample ResNet-50 Split B test (`results_npz_splitB.txt`, 90.10%).
The 14-sample pilot is not a subset or superset of any of these.

**Classification: PARTIALLY VERIFIED.** The claim is consistently documented and (in most places) honestly caveated as a feasibility check, so it is not false. But it has no reproducible evaluation script, no distinct labeled test set, and no saved per-image results, and it is statistically trivial. It must not be presented as a recognition "accuracy" figure on equal footing with the 202-crop or 90.10% evaluations.

---

## Claim 2 Detail: Face recognition accuracy of 77.72% for cosine-only matching

**Source location:** `evaluation/results/cascade_ablation.json` → `cosine_only`: `accuracy=0.7772`, `false_reject_rate=0.1683`, `false_accept_rate=0.0545`. Cited in `CLAIMS_TABLE.md` (C-10) and `paper/PAPER.md`.

**Dataset:** `data/processed/facial_pipeline_results.npz` — 202 test crops, 20 gallery classes. Per `CLAIMS_TABLE.md` C-10 this is a "30% holdout of unaugmented gallery." The NPZ contains 20,130 total samples (confirmed by reproduction probe); the unaugmented originals (`augmentation_index==0`) number ~671, and 30% of that is ~201–202, consistent with the reported N=202.

**Evaluation code:** The `cascade_ablation.json` generator is **absent from the repository**. A search of all `*.py` files for `cascade_ablation`, `cascade_cosine_plus_resnet`, and `resnet_model_threshold` returns only `paper/figures/plot_results.py`, which *reads* the JSON to plot it. There is no script that *writes* it. The cosine-only metric logic, however, is conceptually identical to `evaluate_recognition.py` (argmax cosine similarity vs per-class mean prototypes, accept if ≥ threshold τ=0.55).

**Metric computation (verified):** From the artifact: `tp=157, fp=11, fn=34`, total=202.
- Accuracy = 157/202 = 0.7772 ✓
- Precision = 157/(157+11) = 0.9345 ✓
- Recall = 157/(157+34) = 0.8220 ✓
- FRR = 34/202 = 0.1683 ✓ (claim confirmed)
- FAR = 11/202 = 0.0545 ✓
All values are internally consistent and match the JSON to 4 decimals.

**False reject rate 16.83%:** Confirmed — 34 of 202 true-identity probes were rejected (cosine similarity below 0.55 against their own class prototype). The Wilson 95% CI [12.30, 22.60] is appropriate for this sample size.

**Closed-set caveat:** All 202 probes belong to the 20 enrolled identities. FAR (5.45%) measures wrong-student matches among the enrolled, **not** unknown-impostor accepts. Open-set FAR is unmeasured (`CLAIMS_TABLE.md` C-16 marks open-set testing absent).

**Classification: VERIFIED** (artifact present and internally consistent; FRR 16.83% confirmed). **Reproducibility: PARTIAL** — the generating script is missing, so the result cannot be regenerated from code in the repo.

---

## Claim 3 Detail: Face recognition accuracy of 92.57% for two-stage cascade

**Source location:** `evaluation/results/cascade_ablation.json` → `cascade_cosine_plus_resnet`: `accuracy=0.9257`, `false_reject_rate=0.0198`, `false_accept_rate=0.0545`. Cited in `CLAIMS_TABLE.md` (C-11) and `paper/PAPER.md`.

**Cascade implementation (verified in source):** `vista/vision/recognize.py:_classify_detected_face()` implements the cascade exactly as documented:
1. `_match_student_gallery(face)` loads the enrolled gallery and runs `FaceMatcher` (cosine, threshold 0.55, from `match.py`). If matched, returns immediately.
2. If cosine match fails, `_crop_face()` crops the detection and calls `classify_face()` from `personal_classifier.py` (ResNet-50, loads `best_model_npz_splitB.pth`, threshold 0.60). If softmax confidence ≥ 0.60, returns the classifier result.
3. Otherwise returns `Unknown`.

The ResNet-50 head architecture in `personal_classifier.py` is `Flatten → BatchNorm1d(2048) → ReLU → Dropout(0.4) → Linear(2048,512) → BatchNorm1d(512) → ReLU → Dropout(0.3) → Linear(512,20)` — slightly more regularized than the simplified `FC(2048→512)→ReLU→Dropout(0.3)→FC(512→20)` description in `CLAIMS_TABLE.md` C-04 / the paper abstract (inspection D-2), but functionally equivalent and an improvement, not an error.

**Same 202-crop dataset (verified):** `cascade_ablation.json` shows `total_samples=202` for both `cosine_only` and `cascade_cosine_plus_resnet`, and `gallery_classes=20`. The two rows are a controlled ablation on the **same** test set — the only difference is whether the ResNet-50 fallback stage is active.

**Metric computation (verified):** From the artifact: `tp=187, fp=11, fn=4`, total=202.
- Accuracy = 187/202 = 0.9257 ✓
- Precision = 187/(187+11) = 0.9444 ✓
- Recall = 187/(187+4) = 0.9791 ✓
- F1 = 0.9614 ✓
- FRR = 4/202 = 0.0198 ✓ (claim confirmed)
- FAR = 11/202 = 0.0545 ✓ (**unchanged** from cosine-only)
The cascade recovers **30 false rejects** (34 → 4) **without adding any false accepts** (11 → 11). This is the key ablation result and it is mathematically sound and plausible: the ResNet-50 fallback correctly re-identifies 30 of the 34 cosine-rejected true probes.

**Important nuance:** The production `recognize.py` loads the gallery from the **SQLite database** (`_load_student_gallery()`), whereas the cascade ablation artifact was produced using **NPZ mean-prototype embeddings** as the gallery (the only way to get 202 crops × 20 classes from the NPZ). So the ablation is a faithful *simulation* of the cascade architecture, not a run of the exact production code path. The paper should state this.

**Evaluation code:** The ablation generator is **missing** (see Claim 2). The cascade *logic* is verified present; the *measurement script* is not.

**Classification: VERIFIED** (artifact present and internally consistent; cascade implementation confirmed in `recognize.py`; FRR 1.98% confirmed). **Reproducibility: PARTIAL** — the ablation generator script is absent.

---

## Claim 4 Detail: XGBoost accuracy of 95.7%

**Source location:** The 0.957 figure (macro F1) and ~95% accuracy appear in multiple documents:
- `AUDIT.md` (Section 6, "Historical Run on 200 Balanced Synthetic Records"): *"XGBoost Classifier: Accuracy = 95.00%, Macro F1 = 0.957"* — with the audit finding: *"The risk model F1 dropped from 0.957 to 0.329 due to class imbalance when the dataset was scaled from 200 to 1,000 samples without re-tuning sampling weights or thresholds."*
- `vista/ml/CLAUDE.md` module-state table: *"train.py | Done | Trains XGBoost + LR on synthetic data; XGBoost selected (macro F1 = 0.957)"* — presented as **current** state.
- `vista/README.md`: *"model.pkl (F1=0.957 on synthetic data)"*.
- `vista/PROJECT_REPORT.md`: *"XGBoost (100 trees) | 95% | 0.957 | ✅ Production"* and *"Model performance | XGBoost macro F1 = 0.957 (synthetic validation)"*.
- `vista/PLANB.md` and `docs_backup_final/ROADMAP.md`: *"Macro F1=0.957 validated on synthetic"*.

**Dataset:** An **earlier, smaller, balanced synthetic dataset of ~200 records** with distinct artificial class separation (≈35% LOW / 40% MEDIUM / 25% HIGH). This dataset **no longer exists in the repository** — the current `student_data.csv` has 1000 rows and is severely imbalanced (53.5% HIGH). The `generate_sample_data.py` in the repo even targets N=200 with that balanced profile mix, but the committed CSV is the 1000-row file (see Claim 7).

**Evaluation code:** `vista/ml/train.py` trains XGBoost + Logistic Regression, selects the winner by macro F1, and saves `model.pkl`. The current `evaluate_risk_model.py` (which retrains a fresh XGBoost on the current 1000-row CSV) reproduces **50.0% accuracy / 0.3286 macro F1**, not 95.7%.

**Train/test split & leakage:** The historical 200-row run presumably used a held-out test split (no leakage in the evaluation itself), but the data was synthetic and circularly labeled (labels derived from the same rule-engine thresholds). The 95.7% reflected a dataset with artificial class separation, not a realistic distribution.

**Comparison to the 53.5% majority-class baseline:** Not directly comparable — the 53.5% baseline derives from the current 1000-row imbalanced set (HIGH=53.5%). On the historical balanced 200-row set, the majority-class baseline would have been ~40%, so 95.7% did beat its baseline. The two figures describe **different datasets**, so 95.7% vs 53.5% is not an apples-to-apples comparison.

**Classification: OUTDATED.** The 95.7%/0.957 figure is a real but historical result from a balanced 200-row dataset that no longer exists. It does not describe the current `student_data.csv` (1000 rows), where the model achieves 50.0%. Where the figure is presented as the *current* model performance (notably `vista/ml/CLAUDE.md` and `vista/PROJECT_REPORT.md`'s "✅ Production" row), it is **misleading** (inspection D-1). It does not strictly *contradict* Claim 5 because the two refer to different experiments; the discrepancy is one of staleness and improper present-tense framing.

---

## Claim 5 Detail: XGBoost accuracy of 50% (alternative figure)

**Source location:** `evaluation/results/risk_model_evaluation.json` → `xgboost`: `accuracy=0.5`, `macro_f1=0.3286`. Cited in `CLAIMS_TABLE.md` (C-19, "Disproves legacy 0.957 claim"), `paper/PAPER.md`, `EXHIBITION_KIT.md` ("Honest note: XGBoost macro F1 = 0.3286"), `VIVA_QA.md`.

**Dataset:** `vista/ml/data/student_data.csv` — confirmed 1000 rows (1001 lines incl. header). Full-dataset class distribution (counted): HIGH=535 (53.5%), MEDIUM=405 (40.5%), LOW=60 (6%).

**Evaluation code:** `evaluation/evaluate_risk_model.py`:
- Loads `student_data.csv`; features = `[overall_attendance, recent_attendance, avg_score, recent_score, failed_subjects]`.
- Split: `train_test_split(test_size=0.2, random_state=42, stratify=y)` → train=800, test=200.
- XGBoost: `XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, eval_metric="mlogloss", random_state=42)`.
- Reports accuracy and macro F1 from `sklearn.metrics.classification_report`.

**Data-leakage check:** The split is stratified and held-out (`stratify=y`, `random_state=42`) — there is **no train/test leakage in the evaluation procedure**. The deeper concern is *circularity*: labels are generated by deterministic rules mirroring the production rule engine, so the model is learning an imperfect approximation of a known function on synthetic data (acknowledged in `PAPER_TODO.md` and `EXHIBITION_KIT.md`). That is a validity limitation, not a leakage defect.

**Metric verification (from artifact):** Confusion matrix `[[0,3,9],[1,29,51],[0,36,71]]`.
- Row sums = 12 / 81 / 107 → supports LOW=12, MEDIUM=81, HIGH=107 ✓
- Accuracy = diagonal sum / total = (0+29+71)/200 = 100/200 = 0.5 ✓
- LOW: precision=0, recall=0, F1=0 (model never correctly predicts LOW) ✓
- HIGH: precision=71/131=0.542, recall=71/107=0.6636, F1=0.5966 ✓

**Independent reproduction (performed):** A temporary probe replicated the exact `evaluate_risk_model.py` logic (same CSV, same split, same XGBoost params) and printed results without writing any artifact:
```
rows=1000, full_dist: LOW=60, MEDIUM=405, HIGH=535
train=800 test=200, test_support: LOW=12, MEDIUM=81, HIGH=107
accuracy=0.5, macro_f1=0.3286
confusion_matrix=[[0,3,9],[1,29,51],[0,36,71]]
majority_baseline=0.535
```
The reproduction is **byte-for-byte identical** to `risk_model_evaluation.json`. The result is fully deterministic and reproducible.

**Comparison to the 53.5% baseline:** 50.0% < 53.5%, so XGBoost performs **below** the majority-class baseline (predicting HIGH for all). This is honestly disclosed in the paper and `EXHIBITION_KIT.md`. The production system correctly uses the deterministic rule engine (not XGBoost) for risk decisions (`CLAIMS_TABLE.md` C-22; XGBoost is auxiliary SHAP-only).

**Resolution of the 95.7% vs 50% discrepancy:** They are **not a contradiction** — they refer to different datasets (historical balanced 200-row vs current imbalanced 1000-row). The 50% figure is the **current, authoritative** result. The 95.7% is stale (Claim 4).

**Classification: VERIFIED** (artifact present, internally consistent, and reproduced exactly from the live environment).

---

## Claim 6 Detail: Majority-class baseline of 53.5%

**Source location:** `CLAIMS_TABLE.md` (C-20): *"Majority-Class Baseline | 53.5% [46.59, 60.28] (predicting HIGH for all) | Derived from risk_model_evaluation.json | Support: 12 LOW, 81 MEDIUM, 107 HIGH."* Also `docs_backup_final/REPORT_ch7.md`: *"53.5% HIGH, 40.5% MEDIUM, and only 6.0% LOW."*

**Class distribution verification:**
- Full dataset (1000 rows, counted directly): HIGH=535 (53.5%), MEDIUM=405 (40.5%), LOW=60 (6.0%).
- Test split (200 rows, from artifact + reproduced): HIGH=107 (53.5%), MEDIUM=81 (40.5%), LOW=12 (6.0%).
- The stratified split preserves the proportions: 535/1000 = 107/200 = 53.5% ✓.

**Baseline computation:** The majority class is HIGH. A trivial classifier predicting HIGH for every test sample would be correct on 107/200 = 0.535 = 53.5% of the test set. This is the majority-class baseline.

**Reproduction (performed):** The reproduction probe computed `majority_baseline = max(np.bincount(y_test))/len(y_test) = 107/200 = 0.535`, matching exactly.

**Classification: VERIFIED.** The 53.5% baseline is the HIGH-class prevalence in the (stratified) test split, confirmed both from the artifact supports and by independent counting/reproduction. It correctly contextualizes the XGBoost model's 50.0% as below baseline.

---

## Claim 7 Detail: Synthetic academic dataset of 1,000 samples

**Source location:** `CLAIMS_TABLE.md` (C-18): *"student_data.csv, 1000 generated samples"*; `AUDIT.md`; `generate_sample_data.py` docstring.

**Count verification:** `vista/ml/data/student_data.csv` has **1001 lines including the header = 1000 data rows**. Confirmed by direct line count and by `pandas` load (`len(df)=1000`). The seven columns are `student_id, overall_attendance, recent_attendance, avg_score, recent_score, failed_subjects, risk_label`.

**Is it synthetic?** Yes. It is generated programmatically by `vista/ml/data/generate_sample_data.py`, which:
- Uses a fixed `SEED = 42` and `random.Random(seed)` for reproducibility.
- Draws feature values from profile-specific `uniform` distributions (low/medium/high profiles) plus `gauss(0, 2)` noise.
- Derives `risk_label` via a deterministic `_derive_label()` function mirroring the rule-engine override logic.
There is no real student outcome data; the dataset is entirely synthetic.

**Generation script present?** Yes — `vista/ml/data/generate_sample_data.py` is in the repo.

**Critical reproducibility discrepancy:** The committed generator does **not** reproduce the committed CSV:
1. **Row count mismatch:** The script sets `N_STUDENTS = 200` and its docstring says *"Produces 200 student records"*; `vista/ml/CLAUDE.md` likewise calls it a *"200-student synthetic dataset generator."* The actual CSV has **1000** rows. Running the script as-is would **overwrite** `student_data.csv` with a 200-row file, destroying the current dataset and changing all downstream risk-model results.
2. **Label-logic mismatch:** Row S001 has `overall_attendance=61.68, failed_subjects=3, risk_label=LOW`. The committed `_derive_label()` returns `HIGH` whenever `failed_subjects >= 3`. A row with `failed_subjects=3` cannot be labeled LOW under the current generator logic. This shows the current CSV was produced by an **older/different version** of the generator (different N and/or different label rules) that is no longer committed.

**Classification: VERIFIED** that the dataset is synthetic and contains exactly 1,000 samples, with a generation approach documented. **Reproducibility caveat:** the committed `generate_sample_data.py` is out of sync with the committed `student_data.csv` (200 vs 1000 rows; different label derivation), so the dataset is not regenerable from the script currently in the repo. Re-running the committed script would silently corrupt the dataset.

---

## Claim 8 Detail: Evaluation involving 202 test crops and 20 enrolled identities

**Source location:** `evaluation/results/cascade_ablation.json`: `test_sample_count: 202`, `gallery_classes: 20`. Cited in `CLAIMS_TABLE.md` (C-10/C-11) and `paper/PAPER.md`.

**Evaluation script:** **Missing.** As detailed in Claims 2 and 3, no `*.py` file in the repository writes `cascade_ablation.json`. The four committed evaluation scripts produce the other four JSONs (`evaluate_recognition.py`, `evaluate_risk_model.py`, `benchmark_latency.py`, `evaluate_coach_groundedness.py`); the cascade-ablation generator is absent. This is the single largest reproducibility gap in the project, because it underlies three of the eight audited claims (2, 3, and 8).

**Test-crop count verification:** The artifact's internal arithmetic confirms 202 for both rows: cosine-only `tp+fp+fn = 157+11+34 = 202`; cascade `187+11+4 = 202`. The reported `test_sample_count: 202` is self-consistent.

**20 enrolled identities verification:** `gallery_classes: 20` in the JSON. This matches the 20 USN-named directories actually present in `dataset/` (and `agumented data/`). The NPZ reproduction probe confirmed `unique_classes=20`. The 20 identities are real enrolled AI&ML department students.

**How the test crops were generated:** The crops are the 160×160 face crops stored in `facial_pipeline_results.npz` (array `images`), produced by `regenerate_npz.py` / `facial_pipeline.py` running SCRFD detection on the real camera images in `dataset/`. The 202 are the **unaugmented originals** (`augmentation_index == 0`); augmentation variants (indices 1–29) are used only for training. So the test crops derive from **real student photos**, not synthetic or impostor data. Per `CLAIMS_TABLE.md` C-10, the 202 are a "30% holdout of unaugmented gallery" — 30% of the ~671 unaugmented originals ≈ 201–202, which is consistent with the count.

**Closed-set nature:** Because all 202 crops come from the 20 enrolled identities, this is a **closed-set** evaluation. The 5.45% FAR measures wrong-student matches among the enrolled, not unknown-impostor acceptance. No impostor/open-set test data exists (`CLAIMS_TABLE.md` C-16). This is an important context for interpreting both the cosine-only and cascade numbers.

**Classification: VERIFIED** (the 202-crop / 20-identity counts are confirmed by the artifact's internal arithmetic and by independent dataset inspection; the 20 identities are real enrolled students). **Reproducibility: PARTIAL** — the generating script is missing, so the exact 202-crop split and the cascade-vs-cosine comparison cannot be regenerated from code in the repo.

---

## Additional Claims Found and Verified

Beyond the eight enumerated claims, the following quantitative claims appear in the documentation and were inspected:

**A1 — ResNet-50 test accuracy 90.10% on 20-class Split B (101 samples).** Stated in `README.md`, `CLAIMS_TABLE.md`, `DOCS_SYNC_REPORT.md`, `NEEDS_YOUR_INPUT.md`. **VERIFIED** against `training_results/results_npz_splitB.txt`: test accuracy 0.9010 over 101 test samples (20 classes), best validation 93.07%, final train 96.50%, train/test gap 6.40%. Per-class report confirms weak classes 1DA22AI402 (0/5, F1=0.0) and 1DA24AI403 (3/5, F1=0.4615). This is a **fourth, distinct** face test set (≠14-pilot, ≠107-sweep, ≠202-cascade).

**A2 — Latency: SCRFD+ArcFace 71.23 ms; ResNet-50 CPU 32.5 ms (30.8 FPS); cosine match 100-gallery 1.07 ms.** Stated in `CLAIMS_TABLE.md` C-13. **VERIFIED** against `latency_benchmark.json` (71.23, 32.5/30.8, 1.0693). Hardware Intel i7-13700H (16 logical / 10 physical).

**A3 — Group-photo scaling 77 ms (1 face) → 311 ms (45 faces).** Stated in `CLAIMS_TABLE.md` C-12 as *"Measured on Intel Core i7-13700H CPU, 640x480 frames, fast-path inference."* **VERIFIED against artifact** (`group_photo_scaling`), but with a **caveat**: `benchmark_latency.py` computes these values via an **analytical linear extrapolation** (`fast_path_ms = base_det_time + face_count * (5.0 + per_face_match_time)`; `hybrid_path_ms = fast_path_ms + fallback_count * per_face_resnet_time`), not by directly timing group photos of N faces. The C-12 "Measured" wording is slightly imprecise; these are model-extrapolated from component benchmarks, not end-to-end group-photo measurements.

**A4 — AI coach groundedness 100% (10/10 queries, 0 hallucinations).** Stated in `CLAIMS_TABLE.md` C-31. **VERIFIED-per-artifact** (`coach_groundedness.json`); not independently re-run because it requires a live `OPENROUTER_API_KEY` and an external LLM (`nvidia/nemotron-3.5-super-vl:free`). Scope is narrow (10 queries, 1 student), as the artifact itself notes.

**A5 — 120 API routes; 27 database tables; 3-role RBAC.** Stated in `README.md`, `CLAIMS_TABLE.md` C-26/C-28/C-29, `AUDIT.md`. **VERIFIED-per-prior-audit** (programmatically confirmed in Phases 2–3; `vista/docs/IEEE_PAPER.md`'s older 114/24/6 figures are explicitly superseded).

**A6 — CIE policy thresholds (CIE_MAX=25.0, CIE_ELIGIBILITY_AVG=20.0, best-2-of-3, absent≠0).** Stated in `CLAIMS_TABLE.md` C-25. **VERIFIED** against `vista/backend/app/cie_policy.py` (constants and logic match).

**A7 — "21 students" references in `README.md` Facial Pipeline section.** The README still says *"Reads 21 student subfolders"*, *"~21K images"*, and *"Validate face detection rate across all 21 students."* **STALE/CONTRADICTED by the live `dataset/` directory, which has exactly 20 student folders.** `image_count_report.txt` retains a 21st entry (`1DA22AI010`, 37 images) that is no longer in the dataset. This contradicts the 20-identity claims (7, 8). See Discrepancies.

**A8 — Test-suite pass count.** `CLAIMS_TABLE.md` C-34 states *"27 passing tests (0 failures)"* via `pytest tests/test_features_1_and_2.py tests/test_audit_fixes.py`. The Phase 2–3 inspection footer states *"63/63 tests passing."* These are **not contradictory** — different scopes (C-34 runs only two specific root-level test files yielding 27; the 63 figure includes the broader suite). Worth aligning the documented number with the intended test scope.

---

## Discrepancies and Contradictions

**DC-1 — `vista/ml/CLAUDE.md` presents 0.957 as current (WRONG).** The module-state table says *"XGBoost selected (macro F1 = 0.957)"* in present tense. The current evaluation gives 0.3286. This is a ~3× overstatement of current performance. Also propagated (with varying qualification) in `vista/README.md`, `vista/PROJECT_REPORT.md` ("✅ Production"), `vista/PLANB.md`, and `docs_backup_final/ROADMAP.md`. (Matches inspection D-1.)

**DC-2 — 95.7% (Claim 4) vs 50% (Claim 5): staleness, not a hard contradiction.** They derive from different datasets (historical balanced 200-row vs current imbalanced 1000-row). The 50% is authoritative for the current dataset. The 95.7% is **outdated** and misleading where shown as current. `AUDIT.md` explicitly explains the drop and is the most accurate source.

**DC-3 — `generate_sample_data.py` out of sync with `student_data.csv` (Claim 7).** Script produces 200 rows with label logic that contradicts the CSV (S001: `failed_subjects=3` → LOW, impossible under the committed `_derive_label`). The committed generator cannot reproduce the committed dataset; running it would corrupt the CSV.

**DC-4 — Cascade-ablation generator missing (Claims 2, 3, 8).** `cascade_ablation.json` is an orphan artifact with no producing script. The cascade *logic* exists in `recognize.py`, but the 202-crop ablation measurement cannot be reproduced.

**DC-5 — Threshold sweep (N=107) ≠ cascade ablation (N=202).** Two different test-set construction protocols from the same NPZ (inspection D-7). Worse, the threshold sweep uses Python's randomized `hash(src) % 100` for splitting, making it **non-reproducible across processes** unless `PYTHONHASHSEED` is pinned. Empirically confirmed below.

**DC-6 — README "21 students" vs 20 actual folders (A7).** Stale references to a removed 21st student (`1DA22AI010`).

**DC-7 — Group-photo latency "Measured" vs extrapolated (A3).** `CLAIMS_TABLE.md` C-12 wording implies direct measurement; the values are computed from a linear model of component times.

**DC-8 — ResNet-50 head description simplified (minor).** Paper/C-04 say `FC(2048→512)→ReLU→Dropout(0.3)→FC(512→20)`; actual code adds `BatchNorm1d` at 2048 and 512 and a `Dropout(0.4)`. Functionally equivalent and an improvement (inspection D-2).

---

## Reproducibility Assessment

| Experiment / Claim | Determinism | Generator in repo? | Reproduced? | Assessment |
|---|---|---|---|---|
| Risk model — XGBoost acc=50%, F1=0.3286 (Claims 5, 6; current 50% variant of 4) | Fully deterministic (`random_state=42`, stratified split) | Yes (`evaluate_risk_model.py`) | **Yes — exact match** | **Reproducible** |
| Risk data generation — 1000-row CSV (Claim 7) | Deterministic given the right script | Script present but **out of sync** (200 rows, different labels) | No (would corrupt dataset) | **Not reproducible** from committed script |
| ArcFace threshold sweep, N=107 (context for Claim 2) | **Non-deterministic** (`hash()` randomization) | Yes (`evaluate_recognition.py`) | **No** — fresh run gave N=111, acc=0.7748 vs saved 0.785 | **Not bit-reproducible** across processes |
| Cascade ablation, N=202 (Claims 2, 3, 8) | Unknown | **No** (generator missing) | Cannot attempt | **Not reproducible** (no code) |
| ResNet-50 training, 90.10% Split B (A1) | Mostly deterministic (sklearn rs=42; PyTorch seed not explicitly set) | Yes (`train_from_npz.py`) | Not attempted (heavy CPU training) | Reproducible in principle; minor nondeterminism risk |
| 14-image pilot 100% (Claim 1) | N/A | **No** | No (no script/artifact) | **Not reproducible** (manual feasibility check) |
| Latency benchmarks (A2, A3) | Single-run, no CIs | Yes (`benchmark_latency.py`) | Not attempted | Self-reported; group scaling is extrapolated |
| Coach groundedness 10/10 (A4) | Requires external LLM | Yes (`evaluate_coach_groundedness.py`) | Not attempted (needs API key) | Narrow scope; not generalizable |

**Empirical non-reproducibility of the threshold sweep (DC-5):** A temporary probe replicated `evaluate_recognition.py`'s split logic (`hash(src) % 100`, 70/15/15 gallery/val/test) against the live NPZ with `PYTHONHASHSEED` unset. Results differed from the committed `recognition_threshold_sweep.json`:

| Metric (τ=0.55) | Saved JSON (N=107) | Fresh run (N=111) |
|---|---|---|
| Test N | 107 | 111 |
| Accuracy | 0.7850 | 0.7748 |
| F1 | 0.8796 | 0.8731 |
| FRR | 0.1402 | 0.1622 |
| FAR | 0.0748 | 0.0631 |

The numbers are in the same ballpark (≈15% of ~671 unaugmented originals), confirming the *methodology*, but the exact figures are **not stable across process restarts** because Python randomizes `str.hash` unless `PYTHONHASHSEED` is fixed. The saved JSON is a single-process snapshot. (Note: the cascade ablation's 30% holdout protocol likely avoids this issue, but its script is missing so this cannot be confirmed.)

---

## Recommendations for Strengthening Evidence

1. **Commit the cascade-ablation generator (highest priority).** It produces the evidence for Claims 2, 3, and 8 — three of the eight audited claims — yet is absent. Add a script (e.g., `evaluation/evaluate_cascade.py`) that loads `facial_pipeline_results.npz`, builds a 30% stratified holdout with a **fixed seed**, runs cosine-only and cascade (ResNet-50 fallback) with Wilson CIs, and writes `cascade_ablation.json`.

2. **Make the threshold sweep deterministic.** Replace `hash(src) % 100` in `evaluate_recognition.py` with a seeded split (`np.random.default_rng(seed)`) or a stable hash (`hashlib.md5`), and/or pin `PYTHONHASHSEED` in run instructions. Otherwise the committed `recognition_threshold_sweep.json` cannot be regenerated.

3. **Reconcile `generate_sample_data.py` with `student_data.csv`.** Either (a) update the script to `N_STUDENTS=1000` and align `_derive_label()` with the rules that produced the current CSV (and regenerate), or (b) commit the exact generator version that produced the current 1000-row file. Currently, re-running the committed script would silently overwrite the dataset with a non-matching 200-row file.

4. **Correct/remove the stale 0.957 figure where presented as current.** Update `vista/ml/CLAUDE.md` (module-state table), `vista/PROJECT_REPORT.md` ("✅ Production"), `vista/README.md`, `vista/PLANB.md`, and `docs_backup_final/ROADMAP.md` to either remove 0.957 or clearly mark it as a *historical* 200-row balanced-run result, distinct from the current 0.3286. Keep `AUDIT.md`'s explanatory framing as the model.

5. **De-emphasize the 14-image "100%" as an accuracy figure.** Retain it only as a labeled "feasibility sanity check (2 students, 14 images)" and never alongside the 202-crop or 90.10% numbers as if comparable. Ensure `PITCH_DECK.md` (flagged unqualified in `DOCS_SYNC_REPORT.md`) carries the qualification.

6. **Fix stale "21 students" references** in `README.md`'s Facial Pipeline section and regenerate/trim `image_count_report.txt` to reflect the 20 folders actually present.

7. **Clarify the cascade-ablation simulation vs production path.** State in the paper that the ablation uses NPZ mean-prototype galleries + ResNet-50 fallback (not the production `recognize.py` DB-gallery path), so readers understand it is an architectural simulation.

8. **Soften the latency "Measured" wording.** Note in `CLAIMS_TABLE.md` C-12 that group-photo scaling is extrapolated from component benchmarks via a linear model, not directly timed per face count, and consider adding measured end-to-end group-photo timings if the claim is to stand as "measured."

9. **Add open-set / impostor evaluation** (per `CLAIMS_TABLE.md` C-16 and `PAPER_TODO.md`) so that FAR reflects unknown-identity rejection, not just wrong-enrolled-student matches. This is the most material scientific gap in the vision evaluation.

10. **Pin and document seeds.** Set PyTorch seeds explicitly in `train_from_npz.py` (currently only sklearn `random_state=42` is set) to make the 90.10% ResNet-50 result fully reproducible, and document the `PYTHONHASHSEED` requirement for any script relying on `hash()`.

---

*End of Phase 4 Critical Claim Verification Report.*
