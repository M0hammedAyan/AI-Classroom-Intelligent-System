# FIX_LOG (expanded_v3)

## Step 2 part 1: augmentation regeneration

Script: `regenerate_aug_v3.py` (resumable, marker `regen_progress.json`). Recipe: `build_augmentation_pipeline()` in `vista/vision/facial_pipeline.py` (HorizontalFlip, RandomBrightnessContrast, Rotate limit 15, GaussNoise), SCRFD buffalo_l primary face (highest det score), 160x160, 30 variants per photo, seeded per photo. Note: the task text said ColorJitter and rotate +-10; the original recipe in the helper file is RandomBrightnessContrast and rotate 15, so the helper's recipe was used unchanged.

Stale move: regen students had no augmented folder, so nothing was moved to `agumented data_stale_v1` (folder is gitignored). Added gitignore: agumented data_stale_v1/, training_results/expanded_v3/*.pth, data/processed/*v3*.

### Regenerated students (before -> after)

| USN | dataset photos | aug photo folders before | after | aug files before | after | clean.jpg |
|---|---|---|---|---|---|---|
| 1DA25AI001 | 31 | 0 | 31 | 0 | 930 | 31 |
| 1DA25AI002 | 28 | 0 | 27 | 0 | 810 | 27 |
| 1DA25AI003 | 30 | 0 | 30 | 0 | 900 | 30 |
| 1DA25AI004 | 26 | 0 | 26 | 0 | 780 | 26 |
| 1DA25AI005 | 30 | 0 | 30 | 0 | 900 | 30 |
| 1DA25AI006 | 27 | 0 | 27 | 0 | 810 | 27 |
| 1DA25AI007 | 34 | 0 | 32 | 0 | 960 | 32 |
| 1DA25AI008 | 36 | 0 | 36 | 0 | 1080 | 36 |
| 1DA25AI009 | 36 | 0 | 35 | 0 | 1050 | 35 |
| 1DA25AI010 | 29 | 0 | 25 | 0 | 750 | 25 |

### Original/kept students (augmented folders untouched; clean crops written to training_results/expanded_v3/clean_crops)

| USN | dataset photos | aug folders (unchanged) | aug files (unchanged) | clean crops |
|---|---|---|---|---|
| 1DA23AI001 | 39 | 39 | 1170 | 39 |
| 1DA23AI004 | 29 | 29 | 870 | 29 |
| 1DA23AI005 | 39 | 39 | 1170 | 39 |
| 1DA23AI009 | 35 | 35 | 1050 | 33 |
| 1DA23AI011 | 27 | 27 | 810 | 27 |
| 1DA23AI024 | 29 | 27 | 810 | 27 |
| 1DA23AI025 | 38 | 38 | 1140 | 37 |
| 1DA23AI031 | 34 | 34 | 1020 | 34 |
| 1DA23AI033 | 41 | 41 | 1230 | 41 |
| 1DA23AI036 | 28 | 28 | 840 | 28 |
| 1DA23AI042 | 33 | 33 | 990 | 33 |
| 1DA23AI044 | 38 | 38 | 1140 | 37 |
| 1DA23AI047 | 36 | 36 | 1080 | 36 |
| 1DA23AI049 | 33 | 33 | 990 | 33 |
| 1DA23AI050 | 30 | 30 | 900 | 30 |
| 1DA23AI055 | 36 | 35 | 1050 | 34 |
| 1DA23AI059 | 32 | 32 | 960 | 31 |
| 1DA24AI403 | 33 | 33 | 990 | 33 |
| 1DA24AI404 | 30 | 30 | 900 | 30 |

### Excluded photos (listed in regen_list.json, wrong face or no face; not augmented, no clean crop)

- 1DA25AI002/IMG_20261112_151236.jpg
- 1DA25AI007/IMG_20261112_151626_879.jpg
- 1DA25AI007/IMG_20261112_151629_866.jpg
- 1DA25AI009/IMG_20261112_151927_912.jpg
- 1DA25AI010/IMG_20261112_151043_916.jpg
- 1DA25AI010/IMG_20261112_151257_560.jpg
- 1DA25AI010/IMG_20261112_151303_288.jpg
- 1DA25AI010/IMG_20261112_151314_401.jpg
- 1DA23AI009/IMG20260824111809.jpg
- 1DA23AI009/IMG20260824112017.jpg
- 1DA23AI024/IMG_20260824_105652_141.jpg
- 1DA23AI024/IMG_20260824_105940_864.jpg
- 1DA23AI025/IMG_20260824_105652.jpg
- 1DA23AI044/IMG20260824104642.jpg
- 1DA23AI055/IMG20260824105047.jpg
- 1DA23AI055/IMG20260824105346.jpg
- 1DA23AI059/IMG_6659.jpeg

### No face detected at regeneration time (skipped)

- none

Multi-face photos: the highest-det-score face is used (same as original pipeline). Photos where that face was a different person were already excluded by the audit. No other multi-face photo was altered; largest/central heuristics were not applied because the audit validated the highest-score rule against each student's centroid.

## Step 2 part 2: npz and splits (build_npz_v3.py)

Output: `data/processed/facial_pipeline_results_expanded_v3.npz` (1666.2 MB, gitignored), keys `images` (28830,160,160,3) uint8, `embeddings` (28830,512) float32 (ArcFace R50 via `extract_embeddings_batch`, L2-normalised), `labels`, `metadata` (dicts with source_image, student_id, augmentation_index, original_bbox, det_score), same as the original npz. 29 classes, 930 source photos, 31 samples per photo.

**Classes:** 29 (19 kept + 10 new). 1DA22AI402 is excluded: it has no `dataset/` folder (raw photos removed), so no clean crop can be made for it and it could not have val/test samples. Its old augmented samples are not used. This matches the 29 members stated in the request.

**augmentation_index mapping.** Baseline: 0-29, where index 0 was itself randomly augmented, so val/test were not clean. v3: `0` = clean identity crop (SCRFD primary face, 160x160, no augmentation), `1..30` = the 30 augmented variants. Baseline index k maps to v3 index k+1.
- New 10 students: clean = `agumented data/<USN>/<photo>/clean.jpg`, variants = aug_000..029 -> index 1..30.
- Kept 19 students: clean crop = `training_results/expanded_v3/clean_crops/<USN>/<photo>.jpg` (made in part 1 from the raw photo with the same detector/preprocess). Their on-disk `aug_*.jpg` files are Git-LFS pointer stubs (133 bytes, objects not local), so the 30 variants were reused from the baseline npz (baseline index 0-29 -> v3 index 1-30). bbox/det_score also come from the baseline npz. Nothing was written to the baseline npz or the aug folders.
- Excluded photos (17) have no samples at all, even where an old aug folder exists.

**Splits** (`splits_A.json`, `splits_B.json`, `split_counts.csv`): unit = source photo; per class, one seeded (42) shuffle is shared by both splits, then test = first n_test, val = next n_val, rest train (n_val/n_test = max(3, round(n*ratio))). Val/test use only augmentation_index 0; train uses index 0-30 of its photos. Assertions: disjoint sources and sample indices, val/test only index 0 with one sample per photo, partition covers all photos, plus an MD5 of the raw photo file must not appear on two sides of a split (no duplicate content exists in the data). Every class has at least 3 val and 3 test photos in both splits; no class falls short.

| Split | train photos / samples | val | test |
|---|---|---|---|
| A (80:10:10) | 740 / 22940 | 95 | 95 |
| B (70:15:15) | 654 / 20274 | 138 | 138 |
