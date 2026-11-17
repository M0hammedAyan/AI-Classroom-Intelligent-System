# DIAGNOSIS: 32-class VISTA face classifier (v1 vs baseline)

Merged from `part_a_c_f.md`, `part_b.md`, `part_d.md`, `part_e.md` (same folder). No new analyses, except one spot-check noted below.

## ROOT CAUSES FOUND (ranked by evidence)

1. **Duplicate photo sets under two labels (6 pairs among the new 12, plus 1 pair among the original 20).**
   Proof: `duplicate_photos_cross_student.csv`; `part_d.md` mean-ArcFace cosine 0.9994 to 0.9998 for each pair (next-highest pair is 0.525); `part_b.md` byte-identical photos per pair: 001/009 = 30, 002/007 = 31, 003/012 = 26, 004/008 = 30, 005/011 = 28, 006/010 = 27, and original 1DA22AI402/1DA24AI403 = 33. Total 205 identical-file pairs across 1018 files (813 distinct hashes). Spot-check re-run: 1018 files, 813 distinct MD5, 205 duplicate groups, every group has exactly 2 members, none within one student. The contact sheets for 001 vs 009 and 003 vs 012 show the same man and the same photos.
   Effect: the same face carries two labels, so about 50% is the ceiling on those 12 classes (`part_b.md` section 1). It also breaks the by-photo split, because a photo can sit in train under one label and in val/test under the other (v1 Split A: 58 eval images with an identical file in train under a different USN; Split B: 89; `part_a_c_f.md` section c).
2. **Tiny, noisy val/test sets.** `part_a_c_f.md`: v1 val = 102 (A) and 152 (B) samples, about 3 photos per class, so one photo is about 1% of accuracy. The best epoch was epoch 1 in both baseline and v1 (`part_e.md` section 6, val 0.7157 at epoch 1, 0.6373 at epoch 6). Model selection is on a noisy signal.
3. **Val/test images are not clean.** `part_e.md` section 3: `augmentation_index == 0` is also a random draw of the augmentation pipeline in `regenerate_npz*.py`. About 28.5 of 30 variants are distinct, and no clean crop exists. This adds noise to all reported numbers, in the baseline too.
4. **Label noise from multi-face photos (originals).** `part_b.md` section 4: crop = highest det_score face, no identity check. 62 multi-face photos in the original 20, mostly 1DA23AI025 (19), 1DA23AI001 (14), 1DA23AI033 (11). 61 of 68 multi-face photos have a second face with score at least 0.6. Not confirmed as wrong crops, since only 4 contact sheets were viewed.
5. **Training choices (not v1-vs-baseline defects).** `part_e.md` section 2: one LR for backbone and head, no label smoothing, no class weights.

Ruled out:
- Code differences: `train_expanded.py` vs `train_from_npz.py` differ only in paths, CLI and logging (`part_e.md` section 1). Input size 112, mean/std 0.5, frozen layers, Adam 1e-4, scheduler, loss, seed and patience are identical.
- Image quality of the new 12: resolution, face size, detection score and brightness are close to the originals, and they are slightly sharper (blur median 103.8 vs 68.1) (`part_b.md` section 2). Only the source format differs (all 2296x4080).
- Augmentation recipe: all 1013 photos have exactly 30 variants with aug_idx 0..29; the new 12 were built by the same script in one run (`part_e.md` section 5).
- Split leakage by photo: v1 and v2 pass the index-level assertion (no shared (usn, photo), val/test aug0 only). Leakage only occurs through cause 1.
- Too few photos: none; every class has 26 to 41 photos (`part_a_c_f.md`).

Spot-check discrepancies in the parts: `part_b.md` says "206 duplicate groups" and a photo shared by six students (1DA22AI402, 004, 011, 024, 036, 049). My MD5 re-run gives 205 groups, all with 2 members, so the six-student photo is not confirmed. The figure 205 matches `part_a_c_f.md`. Photo counts per folder (1018 files) include 5 photos with no detected face, which explains 1013 npz photos.

## a) Per-class counts
- 32 classes, 1013 unique (usn, source) photos, 30 rows per photo, 30390 samples. Min 26, median 31, max 41 photos per class. Original-20 mean 33.5, new-12 mean 28.5.
- Classes with fewer than 10 photos: none.
- Per-class train/val/test photos for v1 and v2, A and B: `per_class.csv` and the table in `part_a_c_f.md`.
- Example: 1DA25AI003 and 012 have 26 photos; v1 Split A gave them 21/2/3, v2 gives 20/3/3.

## b) Old 20 vs new 12
- Resolution: orig median 12.39 MP (mixed sizes), new 9.37 MP (all 2296x4080).
- Face crop side: 139.6 vs 143.1 px. Detection score: 0.827 vs 0.833. Brightness: 77.4 vs 81.0. Blur: 68.1 vs 103.8 (new is sharper).
- Detection failures: 3 photos (orig) and 2 (new), negligible.
- Verdict: the new 12 differ in source camera format, not in quality. Quality does not explain the drop. Duplication does.
- Caveat: the new-group statistics come from 6 distinct photo sets, each counted twice.

## c) Leakage
- Split is by (usn, source photo); val/test hold only aug_idx 0 rows. Assertions pass for v1 A/B and v2 A/B (no index overlap, no shared photo).
- Exact-duplicate files across classes: v1 A 58 eval-vs-train, v1 B 89, v2 A 64, v2 B 73 (all across different USNs, none within a USN). Near-duplicates (dHash <= 4, same class): v1 A 3, v1 B 8, v2 A 5, v2 B 7 (burst shots).
- The v1 split log cannot be compared byte for byte, because the A and B logs were written concurrently and interleaved.

## d) Label check
- Contact sheets in `contact_sheets/`. Viewed: 001, 009, 003, 012 (no wrong-person crops, no multi-person folders; some very dark or noisy augmented crops). Not viewed: the other 8 new sheets and the 3 original comparison sheets.
- Suspicious: the duplicated folder pairs above (7 pairs). Not viewed individually: 002/007, 004/008, 005/011, 006/010. They rest on the embedding and filename evidence.
- `embedding_outliers.csv`: low-cosine samples are mostly augmented noise or dark variants of one photo (for example IMG_20261112_151017.jpg in 003/012). Original classes 1DA23AI033, 025, 009 also have near-zero outliers.

## e) train_expanded.py vs train_from_npz.py
- Differences: npz path, output dir, tags, CLI flags (`--npz`, `--smoke`), history JSON, `labels=` in the classification report, one dead line removed. None affects training.
- Identical: 112x112 bilinear resize of the 160x160 RGB crop, mean/std 0.5, ImageNet ResNet-50 (not the ArcFace ONNX model, despite the docstrings), conv1/layer1/layer2 frozen, layer3/layer4/bn1 trainable, Adam 1e-4, ReduceLROnPlateau(0.5, patience 4), CE loss, batch 32, 30 epochs, patience 7, seed 42.
- Augmentation: 30 variants for all 1013 photos, same pipeline for old and new. The claim "aug 0 = original" is false (cause 3).
- Baseline: 20 classes, 671 source photos; "NUM_CLASSES = 21" is a stale constant overwritten in `load_npz`.

## f) Val/test size and stratification
- v1: val 102 / test 102 (A), 152 / 152 (B). About 4 batches, 3 photos per class.
- `split_v2.py` (`split_by_photo`): per-class, at least 2 val and 2 test photos, seed 42, same ordering for A and B. A: train 24150, val 104, test 104 (min 3/3 per class). B: train 21450, val 149, test 149 (min 4/4 per class).
- Classes that cannot satisfy 2 val + 2 test photos: none.
- Caveat: even v2 val/test are about 100 to 150 images, so single-photo swings are about 1%.

## Decision needed (from cause 1)
For each duplicated pair the files cannot say which USN owns the photos. Options per pair: keep one USN and drop the other class (30 classes or fewer), merge the labels, or supply the correct photos for the missing student. Training on all 32 labels as they stand cannot exceed about 50% on those 12 classes. This is a roster decision; it has not been made.
