# S3 Augment

Script: `augment_missing.py` (imports `vista.vision.facial_pipeline` helpers: SCRFD detector, `extract_primary_face`, `preprocess_face`, `augment_face`, baseline pipeline, `AUGMENTATIONS_PER_FACE=30`).
Progress marker: `s3-progress.json` (updated per image).

## Baseline result (missing images only)
| USN | missing imgs | augmented | augs written | no face |
|---|---|---|---|---|
| 1DA23AI024 | 2 | 0 | 0 | 2 |
| 1DA23AI055 | 1 | 0 | 0 | 1 |

Total: 0 images augmented, 3 detection failures, 0 files written. Existing `agumented data` untouched.

## Detection failures (no face)
- 1DA23AI024/IMG_20260824_105652_141.jpg
- 1DA23AI024/IMG_20260824_105940_864.jpg
- 1DA23AI055/IMG20260824105047.jpg

## Skipped: flagged not-in-roster by S1 (not augmented)
1DA25AI001 to 1DA25AI012 (12 students, 348 images). Listed here instead of augmented. They are in `s1-missing.json` but not in the roster or DB. To include them, remove them from the skip set (needs a user decision).

## Students with fewer than 3 usable face images
Among augmented students in S3 scope: 1DA23AI024 and 1DA23AI055 are unchanged (they already have 27 and 35 augmented source images). The 12 skipped students were not evaluated for face usability.

## Advanced recipe (`--advanced`)
Motion Blur, Gaussian Blur, Random Shadow, Downscale. Writes to `agumented_data_advanced_test\`, progress in `s3-progress-advanced.json`. Baseline 30-variant recipe is unchanged.
Unit check on 3 images (the missing images had no detectable face, so the first 3 images of 1DA23AI001 were used as a sample): 3 images x 30 = 90 files written, no errors.

## Status
PARTIAL. All roster-valid missing images were processed (none usable), and the 12 not-in-roster students are skipped pending a decision.
