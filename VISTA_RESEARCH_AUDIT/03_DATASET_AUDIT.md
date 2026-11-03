# Document 3 — Dataset Audit

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 5 (Dataset Audit)
**Basis:** `audit-inspection.md` (Dataset Audit section), `audit-claim-verification.md` (Claims 1, 7, 8), direct directory inspection.

---

## 1. Dataset Inventory Table

| # | Dataset | Location | Type | Samples | Classes | Splits | Leakage Risk | License | Status |
|---|---------|----------|------|---------|---------|--------|-------------|---------|--------|
| D1 | Raw face images | `dataset/` | Real (biometric) | 680 files (~1.94 GB) | 20 students | None at dir level (handled in NPZ) | Low (split on source-image IDs) | None present | [VERIFIED] |
| D2 | Augmented face images | `agumented data/` | Augmented (from D1) | ~20,130 files (~225 MB) | 20 students | None at dir level | Low (intermediate artifact) | None present | [VERIFIED] |
| D3 | Compiled embeddings NPZ | `data/processed/facial_pipeline_results.npz` | Processed (from D1+D2) | ~20,400 (680×30) | 20 students | Dynamic (train_from_npz.py) | Controlled (aug_idx=0 for val/test) | None present | [VERIFIED] |
| D4 | Synthetic risk data | `vista/ml/data/student_data.csv` | Synthetic | 1000 rows | 3 (LOW/MED/HIGH) | 80/20 stratified (rs=42) | Circular (labels from rule engine) | None present | [VERIFIED] |
| D5 | UCI Student Performance | Not in repo (external) | Real | — | — | — | N/A | External (referenced by `validate_uci.py` only) | [DOCUMENTED ONLY] |

---

## 2. Per-Dataset Detailed Analysis

### Dataset D1: Raw Face Images (`dataset/`)

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Location | `dataset/` | [VERIFIED] |
| Total files | 680 raw images | [VERIFIED — `audit-inspection.md` Dataset Audit section] |
| Total size | ~1.94 GB | [VERIFIED] |
| Identities | 20 students (USN-named directories) | [VERIFIED — directory listing confirms exactly 20 folders] |
| File naming | `IMG_YYYYMMDD_HHMMSS.jpg/jpeg` — timestamped camera captures | [VERIFIED] |
| Per-student count | 27–41 images (min: 1DA23AI011=27-28, max: 1DA23AI033=41) | [VERIFIED — `training_results/image_count_report.txt`] |
| Image type | Raw camera JPEGs, ~2–4 MB each | [VERIFIED] |
| Split method | No pre-existing split; done dynamically by `train_from_npz.py` on `(usn, source_image)` pairs | [VERIFIED — `train_from_npz.py` docstring + `audit-claim-verification.md`] |
| Augmentation | None in this directory | [VERIFIED] |
| Leakage risk | Low — splitting on source-image identifiers prevents augmented variants crossing partitions | [VERIFIED — `train_from_npz.py` has `assert_no_leakage`] |

#### Class Distribution (Per-Student Raw Image Counts)

| USN | Raw Images | Evidence |
|-----|-----------|---------|
| 1DA22AI402 | 34-35 | [VERIFIED — `image_count_report.txt`] |
| 1DA23AI001 | 39 | [VERIFIED] |
| 1DA23AI004 | 29-30 | [VERIFIED] |
| 1DA23AI005 | 39 | [VERIFIED] |
| 1DA23AI009 | 35 | [VERIFIED] |
| 1DA23AI011 | 27-28 | [VERIFIED — minimum] |
| 1DA23AI024 | 27-30 | [VERIFIED] |
| 1DA23AI025 | 38 | [VERIFIED] |
| 1DA23AI031 | 34 | [VERIFIED] |
| 1DA23AI033 | 41 | [VERIFIED — maximum] |
| 1DA23AI036 | 28-29 | [VERIFIED] |
| 1DA23AI042 | 33 | [VERIFIED] |
| 1DA23AI044 | 38 | [VERIFIED] |
| 1DA23AI047 | 36 | [VERIFIED] |
| 1DA23AI049 | 33-34 | [VERIFIED] |
| 1DA23AI050 | 30 | [VERIFIED] |
| 1DA23AI055 | 36 | [VERIFIED] |
| 1DA23AI059 | 32 | [VERIFIED] |
| 1DA24AI403 | 33 | [VERIFIED] |
| 1DA24AI404 | 30 | [VERIFIED] |

**Note:** `image_count_report.txt` also lists `1DA22AI010` (37 images, 21st entry) which is NOT present in the current `dataset/` directory. This student was removed; the report is stale. [CONTRADICTED — `audit-inspection.md` D-6, `audit-claim-verification.md` A7/DC-6. The README still references "21 students" which is incorrect — current dataset has exactly 20.]

#### Data Leakage Assessment (D1)

Splitting is performed on unique `(usn, source_image)` pairs before augmentation, with runtime assertions verifying disjoint train/val/test sets. Augmentation is applied only to training-partition source images. This is a sound leakage prevention strategy. [VERIFIED — `train_from_npz.py` `assert_no_leakage`, `audit-claim-verification.md` Claim 8 detail]

#### Quality Limitations

- Small scale: 20 students, 27-41 images each — pilot-scale only.
- Real biometric data of actual enrolled students (not a public dataset).
- Variable image quality (raw camera captures, uncontrolled lighting/pose).
- No metadata beyond directory name and capture timestamp.
- No demographic annotation for fairness analysis.
- No consent records stored alongside images (see Document 7).

### Dataset D2: Augmented Face Images (`agumented data/`)

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Location | `agumented data/` (sic — missing one 'g') | [VERIFIED — consistent spelling throughout codebase] |
| Total files | ~20,130 JPEG images | [VERIFIED] |
| Total size | ~225 MB | [VERIFIED] |
| Identities | 20 students (same USN directories as D1) | [VERIFIED] |
| Structure | Per-student → per-source-image subdirectory → `aug_000.jpg` through `aug_029.jpg` | [VERIFIED] |
| Augmentation multiplier | 30 variants per source image | [VERIFIED — 30 files per subdirectory] |
| Augmentation types | HorizontalFlip, ColorJitter, RandomRotate(±10°), GaussianNoise (Albumentations) | [VERIFIED — `vista/vision/facial_pipeline.py`, `audit-inspection.md`] |
| Per-student count | 810–1,230 files (proportional to raw image count × 30) | [VERIFIED] |
| Relationship to D1 | Each `aug_NNN.jpg` derived from exactly one raw image in D1 | [VERIFIED] |
| Split method | Not applied at this level — handled by `train_from_npz.py` | [VERIFIED] |
| Leakage risk | Low — this is an intermediate artifact; leakage is controlled at the NPZ/train-split level | [VERIFIED] |

#### Augmentation Details

The augmentation pipeline (Albumentations) applies:
- HorizontalFlip (p=0.5)
- ColorJitter (brightness/contrast/saturation ±20%)
- RandomRotate (±10 degrees)
- GaussianNoise

30 augmented variants are generated per source image, significantly expanding the training set from ~680 originals to ~20,400 samples. [VERIFIED — `vista/vision/facial_pipeline.py`]

#### Data Leakage Assessment (D2)

The augmented directory itself has no train/test split. Leakage is prevented at the NPZ/training level: `train_from_npz.py` splits on source-image IDs first, then applies augmentation only to training-partition images. Validation and test sets strictly comprise unaugmented originals (`augmentation_index=0`). [VERIFIED — `train_from_npz.py` docstring, `audit-claim-verification.md`]

### Dataset D3: Compiled Embeddings NPZ (`data/processed/`)

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Location | `data/processed/facial_pipeline_results.npz` | [VERIFIED] |
| Size | 1.15 GB | [VERIFIED] |
| Arrays | `images` (N,160,160,3) uint8; `embeddings` (N,512) float32; `labels` (N,) USN strings; `metadata` (N,) dicts | [VERIFIED — `audit-inspection.md`] |
| Metadata fields | `source_image`, `student_id`, `augmentation_index` (0-29), `original_bbox`, `det_score` | [VERIFIED] |
| Total samples | ~20,400 (680 originals × 30 augmentations) | [VERIFIED — reproduction probe in `audit-claim-verification.md` confirmed 20,130 total] |
| Gallery classes | 20 | [VERIFIED — `unique_classes=20` confirmed] |
| Unaugmented originals | ~671 (`augmentation_index=0`) | [VERIFIED — `audit-claim-verification.md` Claim 8] |
| Test set for threshold sweep | N=107 (15% of unaugmented, hash-based split) | [VERIFIED — `recognition_threshold_sweep.json`] |
| Test set for cascade ablation | N=202 (30% holdout of unaugmented) | [VERIFIED — `cascade_ablation.json`] |
| Regeneration | `regenerate_npz.py` re-runs SCRFD+ArcFace on raw `dataset/` images | [VERIFIED] |

#### Split Methodology

Two different evaluation protocols use different splits from the same NPZ:

1. **Threshold sweep** (`evaluate_recognition.py`): 70/15/15 gallery/val/test split using `hash(src) % 100` — this is **non-deterministic across Python processes** unless `PYTHONHASHSEED` is pinned. [PARTIALLY VERIFIED — `audit-claim-verification.md` DC-5 confirms fresh run gave N=111 vs saved N=107]

2. **Cascade ablation** (generator script MISSING): 30% holdout of unaugmented originals, stratified. The generating script is absent from the repo, so this split cannot be reproduced from code. [PARTIALLY VERIFIED — `audit-claim-verification.md` DC-4]

3. **ResNet-50 training** (`train_from_npz.py`): Stratified split on unique `(usn, source_image)` pairs (Split B: 70/15/15). Augmentation applied only to training partition. Runtime `assert_no_leakage` verifies disjoint sets. [VERIFIED]

#### Data Leakage Assessment (D3)

The leakage prevention strategy is sound: splitting on source-image identifiers before augmentation, with augmented variants (`augmentation_index` 1-29) restricted to training and unaugmented originals (`augmentation_index=0`) used for val/test. The runtime assertion `assert_no_leakage` explicitly verifies set disjointness. [VERIFIED — `train_from_npz.py`]

**However:** the non-deterministic hash-based split in `evaluate_recognition.py` means the threshold sweep results are not stable across process restarts. A fresh run produced different metrics (N=111, acc=0.7748 vs saved N=107, acc=0.785). [CONTRADICTED for reproducibility — `audit-claim-verification.md` DC-5, Table in Reproducibility Assessment]

### Dataset D4: Synthetic Risk Training Data (`vista/ml/data/`)

| Attribute | Value | Evidence |
|-----------|-------|---------|
| File | `student_data.csv` | [VERIFIED] |
| Size | 36 KB | [VERIFIED] |
| Rows | 1000 (1001 lines incl. header) | [VERIFIED — line count + pandas load, `audit-claim-verification.md` Claim 7] |
| Columns | 7: `student_id`, `overall_attendance`, `recent_attendance`, `avg_score`, `recent_score`, `failed_subjects`, `risk_label` | [VERIFIED] |
| Features | 5: `overall_attendance`, `recent_attendance`, `avg_score`, `recent_score`, `failed_subjects` | [VERIFIED — `evaluate_risk_model.py`] |
| Target | `risk_label` (LOW/MEDIUM/HIGH) | [VERIFIED] |
| Generation | `generate_sample_data.py` (seed=42) | [VERIFIED — script present] |
| Real data | NONE — entirely synthetic | [VERIFIED] |
| Split | 80/20 stratified, random_state=42 (train=800, test=200) | [VERIFIED — `evaluate_risk_model.py`] |

#### Class Distribution

| Class | Full Dataset | Count | % | Test Split | Count | % | Evidence |
|-------|-------------|-------|---|-----------|-------|---|---------|
| HIGH | 535 | 53.5% | | HIGH | 107 | 53.5% | [VERIFIED — `audit-claim-verification.md` Claim 6, reproduced] |
| MEDIUM | 405 | 40.5% | | MEDIUM | 81 | 40.5% | [VERIFIED] |
| LOW | 60 | 6.0% | | LOW | 12 | 6.0% | [VERIFIED] |
| **Total** | **1000** | **100%** | | **Total** | **200** | **100%** | [VERIFIED — stratified split preserves proportions] |

**Class imbalance is severe:** LOW class represents only 6% of samples (12 in test), which explains the XGBoost model's complete failure on LOW (F1=0.000). [VERIFIED — `risk_model_evaluation.json`, reproduced in Phase 4]

#### Label Generation (Circular Signal)

Labels are generated by `generate_sample_data.py` using a deterministic `_derive_label()` function that mirrors the rule engine's override logic. This creates a **circular training signal**: the XGBoost model learns an imperfect approximation of the same deterministic function used for production risk decisions. [VERIFIED — `audit-inspection.md` Dataset D4, `audit-claim-verification.md` Claim 7]

#### Critical Reproducibility Discrepancy

The committed `generate_sample_data.py` does NOT reproduce the committed `student_data.csv`: [CONTRADICTED — `audit-claim-verification.md` DC-3]

1. **Row count mismatch:** Script sets `N_STUDENTS = 200` and docstring says "Produces 200 student records." The actual CSV has 1000 rows. Running the script would overwrite the CSV with a 200-row file. [VERIFIED — script inspected]

2. **Label-logic mismatch:** Row S001 has `overall_attendance=61.68, failed_subjects=3, risk_label=LOW`. The committed `_derive_label()` returns `HIGH` whenever `failed_subjects >= 3`. A row with `failed_subjects=3` cannot be labeled LOW under the current generator. [VERIFIED — `audit-claim-verification.md` Claim 7 detail]

This means the current CSV was produced by an older/different version of the generator that is no longer committed. Re-running the committed script would silently corrupt the dataset.

#### Data Leakage Assessment (D4)

The train/test split itself (stratified, `random_state=42`) has **no leakage** — it is a proper held-out split. The deeper concern is **circularity**: labels derive from the same rule engine used in production, so the model learns a known function rather than discovering novel patterns. This is a validity limitation, not a leakage defect. [VERIFIED — `audit-claim-verification.md` Claim 5 detail]

#### Quality Limitations

- Entirely synthetic — no real student outcomes.
- Circular labeling (labels from rule engine, model learns rule engine).
- Severe class imbalance (6% LOW).
- Generator out of sync with committed CSV (cannot reproduce).
- Row S001 label contradicts current generator logic.
- Only 5 features — no temporal, behavioral, or demographic features.
- No real longitudinal data validating risk predictions against actual outcomes.

---

## 3. Face Recognition Dataset: 202-Crop Evaluation Set and 20-Identity Enrollment Set

### 20-Identity Enrollment Set

The enrollment gallery consists of 20 real enrolled AI&ML department students at Dr. Ambedkar Institute of Technology, Bengaluru. Each student's USN-named directory in `dataset/` contains 27-41 raw camera images. [VERIFIED — directory listing, `audit-claim-verification.md` Claim 8]

These are real biometric data of actual students, not a public benchmark dataset. The 20 identities are the same across D1 (raw), D2 (augmented), and D3 (NPZ). [VERIFIED]

**No consent records are stored alongside the images.** A consent form template exists (`vista/docs/CONSENT_FORM.md`) but contains placeholder fields (`[Guide Name]`, `[Department/Faculty Committee Name]`) and has not been filled with actual approvals. [PARTIALLY VERIFIED — see Document 7]

### 202-Crop Evaluation Set

| Attribute | Value | Evidence |
|-----------|-------|---------|
| Test samples | 202 | [VERIFIED — `cascade_ablation.json`: `test_sample_count: 202`, confirmed by internal arithmetic: 157+11+34=202] |
| Gallery classes | 20 | [VERIFIED — `cascade_ablation.json`: `gallery_classes: 20`] |
| Construction | 30% holdout of unaugmented originals (`augmentation_index=0`) | [VERIFIED — `CLAIMS_TABLE.md` C-10, ~30% of ~671 originals ≈ 201-202] |
| Source | `facial_pipeline_results.npz` — real SCRFD detections from 20 enrolled students | [VERIFIED — `audit-claim-verification.md` Claim 8] |
| Crop type | 160×160 face crops (NPZ `images` array) | [VERIFIED — `audit-inspection.md`] |
| Closed-set | Yes — all 202 crops belong to enrolled identities | [VERIFIED — `audit-claim-verification.md` Claim 8] |
| Impostor set | None — no un-enrolled faces | [VERIFIED — `CLAIMS_TABLE.md` C-16 marks absent] |

**Key limitation:** This is a **closed-set** evaluation. The 5.45% FAR measures wrong-student matches among the enrolled, NOT unknown-impostor acceptance. Open-set FAR is unmeasured. [VERIFIED — `audit-claim-verification.md` Claims 2, 3, 8]

**Reproducibility gap:** The generator script for `cascade_ablation.json` is **missing from the repository**. The cascade logic is verified in `recognize.py`, but the 202-crop ablation measurement cannot be regenerated from code. [PARTIALLY VERIFIED — `audit-claim-verification.md` DC-4]

**Important nuance:** The production `recognize.py` loads the gallery from the SQLite database, whereas the cascade ablation used NPZ mean-prototype embeddings as the gallery. So the ablation is a faithful *simulation* of the cascade architecture, not a run of the exact production code path. [DOCUMENTED ONLY — `audit-claim-verification.md` Claim 3 detail]

### Relationship to Other Face Test Sets

The repository contains four distinct face test sets, which must not be conflated: [VERIFIED — `audit-claim-verification.md` Claim 1 detail]

| Test Set | N | Classes | Source | Purpose | Reproducible? |
|----------|---|---------|--------|---------|---------------|
| 14-image pilot | 14 | 2 | Manual | Feasibility check | [UNVERIFIED — no script] |
| Threshold sweep | 107 | 20 | NPZ (hash split) | Threshold optimization | [PARTIALLY VERIFIED — non-deterministic hash] |
| Cascade ablation | 202 | 20 | NPZ (30% holdout) | Cascade vs. cosine ablation | [PARTIALLY VERIFIED — generator missing] |
| ResNet-50 Split B | 101 | 20 | NPZ (stratified split) | Classifier test accuracy | [VERIFIED — `train_from_npz.py`] |

---

## 4. Academic Risk Dataset: 1,000-Sample Synthetic Dataset

### Summary

The academic risk dataset is `vista/ml/data/student_data.csv`, containing exactly 1000 synthetic student records with 5 features and a 3-class risk label (LOW/MEDIUM/HIGH). The dataset is entirely synthetic, generated by `generate_sample_data.py`. [VERIFIED — `audit-claim-verification.md` Claim 7]

### Class Distribution and Imbalance

- HIGH: 535 (53.5%) — majority class
- MEDIUM: 405 (40.5%)
- LOW: 60 (6.0%) — severe minority

[VERIFIED — counted directly and reproduced in Phase 4]

The majority-class baseline (predicting HIGH for all) yields 53.5% accuracy. The XGBoost model achieves 50.0%, which is **below** this baseline. [VERIFIED — `risk_model_evaluation.json`, reproduced exactly]

### Split Methodology

- Split: `train_test_split(test_size=0.2, random_state=42, stratify=y)` → train=800, test=200
- Stratified: preserves class proportions (53.5/40.5/6.0 in both train and test)
- Deterministic: `random_state=42` makes this fully reproducible

[VERIFIED — `evaluate_risk_model.py`, reproduced byte-for-byte in Phase 4]

### Confusion Matrix (XGBoost on Test Set, N=200)

```
              Predicted
              LOW  MED  HIGH
Actual LOW  [  0    3     9  ]   (12 samples)
Actual MED  [  1   29    51  ]   (81 samples)
Actual HIGH [  0   36    71  ]   (107 samples)
```

[VERIFIED — `risk_model_evaluation.json`, reproduced exactly in Phase 4]

- LOW class: 0 correct out of 12 (F1=0.000) — model completely fails on minority class
- MEDIUM class: 29 correct out of 81 (recall 35.80%, F1=0.3893)
- HIGH class: 71 correct out of 107 (recall 66.36%, F1=0.5966)
- Overall accuracy: (0+29+71)/200 = 50.0%

[VERIFIED — all values match artifact and reproduction]

### Data Leakage Assessment

**No split-level leakage** — the stratified held-out split is procedurally correct. [VERIFIED]

**Circularity concern** — labels derive from the same deterministic rule engine used in production. The XGBoost model learns an imperfect approximation of a known function rather than discovering novel predictive patterns. This is acknowledged in the paper and PAPER_TODO.md. [VERIFIED — `audit-claim-verification.md` Claim 5 detail]

**Generator out of sync** — the committed `generate_sample_data.py` (200 rows, different label logic) cannot reproduce the committed 1000-row CSV. Re-running would corrupt the dataset. [CONTRADICTED — `audit-claim-verification.md` DC-3]

### Quality Limitations

1. Entirely synthetic — no real student outcome data validates the risk predictions. [VERIFIED]
2. Circular labeling creates a tautological training signal. [VERIFIED]
3. Severe class imbalance (6% LOW) causes minority-class failure. [VERIFIED]
4. Generator script cannot reproduce the committed dataset. [CONTRADICTED]
5. Only 5 tabular features — no temporal dynamics, behavioral data, or demographic context. [VERIFIED]
6. No cross-validation — single 80/20 split only. [VERIFIED]
7. UCI dataset referenced by `validate_uci.py` is external (Portuguese secondary school data, not Indian college context) and is not included in the repo. [DOCUMENTED ONLY]

---

## 5. Specific Data Leakage Findings

### Finding 1: Subject Overlap Between Partitions

**Status: NO LEAKAGE FOUND** [VERIFIED]

The face recognition training pipeline (`train_from_npz.py`) splits on unique `(usn, source_image)` pairs before applying augmentation. Runtime assertions verify disjoint train/val/test sets. A student's augmented images cannot appear in both train and test because the split is at the source-image level. [VERIFIED — `train_from_npz.py` `assert_no_leakage`]

### Finding 2: Augmented Samples Crossing Partitions

**Status: NO LEAKAGE FOUND** [VERIFIED]

Augmentation (30 variants) is applied exclusively to source images in the training partition. Validation and test sets strictly comprise unaugmented originals (`augmentation_index=0`). [VERIFIED — `train_from_npz.py`]

### Finding 3: Non-Deterministic Threshold Sweep Split

**Status: REPRODUCIBILITY RISK (not leakage per se)** [PARTIALLY VERIFIED]

`evaluate_recognition.py` uses `hash(src) % 100` for splitting, which is non-deterministic across Python processes (Python randomizes `str.hash` unless `PYTHONHASHSEED` is pinned). A fresh run produced different metrics (N=111 vs saved N=107). This is not data leakage but makes the result non-reproducible. [VERIFIED — `audit-claim-verification.md` DC-5]

### Finding 4: Risk Model Circular Training Signal

**Status: VALIDITY CONCERN (not leakage)** [VERIFIED]

Labels in `student_data.csv` are generated by deterministic rules mirroring the production rule engine. The XGBoost model learns an approximation of the same function used for production decisions. This is not data leakage but a fundamental validity limitation — the model cannot discover patterns beyond what the rule engine already encodes. [VERIFIED — `audit-claim-verification.md` Claim 5]

### Finding 5: Missing Cascade Ablation Generator

**Status: REPRODUCIBILITY GAP** [PARTIALLY VERIFIED]

The script that generates `cascade_ablation.json` (N=202) is absent from the repo. The cascade logic is verified in `recognize.py`, but the exact 202-crop split and the cosine-vs-cascade comparison cannot be regenerated. [VERIFIED — `audit-claim-verification.md` DC-4]

---

## 6. Dataset Quality Limitations (Consolidated)

| Limitation | Dataset(s) Affected | Evidence | Impact |
|-----------|---------------------|---------|--------|
| Pilot-scale (20 students only) | D1, D2, D3 | [VERIFIED] | Limits generalizability claims |
| No public benchmark comparison | D1-D3 | [VERIFIED] | Cannot compare to LFW, IJB, etc. |
| Closed-set only (no impostors) | D3 | [VERIFIED] | FAR does not measure unknown-identity rejection |
| Non-deterministic split | D3 (threshold sweep) | [VERIFIED] | Results not reproducible across processes |
| Missing generator script | D3 (cascade ablation) | [VERIFIED] | Cannot reproduce cascade ablation results |
| Synthetic data only | D4 | [VERIFIED] | No real outcome validation |
| Circular labeling | D4 | [VERIFIED] | Model learns known function, not novel patterns |
| Severe class imbalance | D4 | [VERIFIED] | Minority class failure (LOW F1=0.000) |
| Generator out of sync | D4 | [CONTRADICTED] | Dataset not regenerable from committed code |
| No demographic annotation | D1-D3 | [VERIFIED] | No fairness/bias analysis possible |
| No real longitudinal outcomes | D4 | [VERIFIED] | Risk predictions not validated against actual failure |

---

## 7. Dataset Licensing and Consent Information

### Licensing

| Dataset | License | Evidence |
|---------|---------|---------|
| D1 (raw face images) | **None present** | [UNVERIFIED — no LICENSE file, no README in `dataset/`] |
| D2 (augmented) | **None present** | [UNVERIFIED — no LICENSE in `agumented data/`] |
| D3 (NPZ) | **None present** | [UNVERIFIED — no LICENSE in `data/processed/`] |
| D4 (synthetic risk) | **None present** | [UNVERIFIED — no LICENSE in `vista/ml/data/`] |
| InsightFace models | Apache 2.0 (InsightFace project) | [DOCUMENTED ONLY — standard InsightFace license, not verified in repo] |

**Assessment:** No dataset in the repository has an accompanying license file. The face images are real biometric data of actual students, making licensing and consent a critical gap. [UNVERIFIED]

### Consent

A consent form template exists at `vista/docs/CONSENT_FORM.md`. Key observations: [VERIFIED — file inspected directly]

**What the consent form claims:**
- "3-5 facial photographs" collected (actual: 27-41 per student) [CONTRADICTED — consent form says 3-5, dataset has 27-41]
- "Photos deleted after processing" (actual: ~1.94 GB of raw photos retained in `dataset/`) [CONTRADICTED — photos are not deleted]
- "Face embedding stored in encrypted database" (actual: SQLite stores embeddings as plaintext JSON, no encryption) [CONTRADICTED — no encryption at rest]
- "Data retained for 8 weeks + 4 weeks analysis" (actual: data retained indefinitely as of audit) [CONTRADICTED]
- "Local only — data never leaves college server" (actual: if `LLM_USE_API=true`, aggregated academic numbers sent to OpenRouter, though no PII) [PARTIALLY VERIFIED — PII stripped, but data does leave server for LLM]

**What the consent form does NOT confirm:**
- Institutional ethics approval: placeholder text `[Department/Faculty Committee Name]` — never filled. [UNVERIFIED]
- Faculty advisor: placeholder text `[Guide Name]` — never filled. [UNVERIFIED]
- Actual signed consent forms: no signed copies in the repository. [UNVERIFIED]
- Consent for the LLM coaching feature: consent form mentions only face data, not LLM interaction. [UNVERIFIED]

**Critical discrepancies between consent form and implementation:**
1. Consent form says 3-5 photos; dataset has 27-41 per student.
2. Consent form says photos deleted after processing; photos retained.
3. Consent form says encrypted database; SQLite is plaintext.
4. Consent form says 12-week retention; data retained indefinitely.

[VERIFIED — all discrepancies confirmed by comparing `CONSENT_FORM.md` text with actual `dataset/` contents, `db.py` (no encryption), and file presence]

---

*End of Document 3 — Dataset Audit*
