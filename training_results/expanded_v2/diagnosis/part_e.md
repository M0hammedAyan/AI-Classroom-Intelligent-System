# Part E: train_expanded.py vs train_from_npz.py, and augmentation recipe check

Commands: `git diff --no-index -U0 train_from_npz.py train_expanded.py` (and the same for `regenerate_npz.py` vs `regenerate_npz_expanded.py`), plus `part_e_check.py` and `part_e_orig.py` in this folder (read-only on the npz files).

## 1. Every difference between train_from_npz.py and train_expanded.py

The diff is 41 insertions and 30 deletions. None of them touches the model, preprocessing, optimizer, scheduler, loss, split logic, seed or patience.

| Item | train_from_npz.py (baseline) | train_expanded.py (v1) | Training impact |
|---|---|---|---|
| NPZ path | `facial_pipeline_results.npz` | `facial_pipeline_results_expanded.npz` (`--npz` flag) | Data only |
| Output dir | `training_results/` | `training_results/expanded/` | None |
| Tags | `npz_splitA/B` | `expanded_splitA/B` | None |
| `NUM_CLASSES` constant | 21 (overwritten in `load_npz`) | 0 (overwritten in `load_npz`) | None. Both derive it from the labels (see 2) |
| CLI | `--split A|B|both`, `--epochs` | `--split A|B` required, plus `--npz`, `--smoke` | None |
| History JSON | not written | written each epoch (`epoch_seconds` too) | None |
| `--smoke` subset | none | truncates to 64/32/32 samples, only when flag set | None for real runs |
| `classification_report` | no `labels=` argument | `labels=range(NUM_CLASSES)` | Report only. Prevents a crash if a class is missing from test |
| `tr_cls` line | dead, slow `records.index` line plus the fast one | only the fast one | None |
| `import json` | absent | added | None |

## 2. Settings that are identical in both files

| Setting | Both files |
|---|---|
| Input size | `IMG_SIZE = 112`. `NPZFaceDataset.__getitem__` does `Image.fromarray(img).resize((112,112), BILINEAR)` on the 160x160 npz crop |
| Normalisation | mean `[0.5]*3`, std `[0.5]*3` |
| Channel order | npz crops are RGB (`cv2.cvtColor(BGR2RGB)` in the regenerate scripts). PIL and ToTensor keep RGB. There is no BGR path in training. BGR is used only for InsightFace detection and embeddings (RGB2BGR before `get_feat`), which this trainer does not use. |
| Backbone | `resnet50(IMAGENET1K_V1)`. This is not the ArcFace ONNX model, although the docstrings say "ArcFace preprocessing" |
| Frozen layers | everything frozen, then `layer3`, `layer4` and `bn1` unfrozen. `conv1`, `layer1` and `layer2` stay frozen, and so do their BN layers. |
| Head | Flatten, BN1d(2048), ReLU, Dropout 0.4, Linear 2048-512, BN1d, ReLU, Dropout 0.3, Linear 512-num_classes |
| Trainable / frozen params | v1 log: 23,133,856 trainable, 1,444,800 frozen (32 classes). The head's last layer is 512 x num_classes, so the baseline's 20-class count differs only by 12 x 513 = 6,156 parameters. |
| Optimizer | Adam, a single lr 1e-4 for all trainable parameters, no weight decay |
| Scheduler | `ReduceLROnPlateau(mode="max", factor=0.5, patience=4)` on val acc |
| Loss | `CrossEntropyLoss()`, no label smoothing, no class weights |
| Batch / epochs / patience | 32 / 30 / 7 (early stopping on best val acc) |
| Train-time augmentation (torchvision) | RandomHorizontalFlip(0.3), ColorJitter(brightness 0.15, contrast 0.15). Val and test: ToTensor and Normalize only. |
| Seed | 42. `seed_all` sets random, numpy, torch and CUDA, with cudnn deterministic. |
| Class mapping | `sorted(set(labels))` mapped to 0..K-1. `NUM_CLASSES = len(KNOWN_USNS)` in `load_npz`. The v1 log confirms 32 classes discovered, in sorted order. |
| Split | `split_npz`: unique `(usn, source_image)` pairs, two stratified `train_test_split` calls (test first, then val) with `random_state=42`. Train takes all 30 variants of its sources. Val and test take only `aug_idx == 0` of their sources. |
| Leakage assertion | same `assert_no_leakage` (disjoint indices, `aug_idx == 0` in val/test) |
| Model selection | best val acc checkpoint. Test is evaluated once. |

Conclusion: the code path is a copy. The 32-class run differs from the baseline only through the data and the number of classes. Code settings do not explain the drop.

Baseline check (`baseline_before_expansion/results_npz_splitA.txt` and `s2-baseline-hparams.md`): ResNet-50 ImageNet, Adam 1e-4, batch 32, patience 7, 112x112, mean 0.5 / std 0.5, seed 42. This matches the expanded trainer. The baseline npz has 20 classes and 671 source images (checked with `part_e_orig.py`), so "NUM_CLASSES = 21" in the baseline file is only a stale constant.

## 3. How val and test sets are formed (both files)

Val and test come from source photos not used in train, but they are the `augmentation_index == 0` variant. The docstrings and the regenerate script header say "0 = original / no stochastic transform". That is wrong. In both `regenerate_npz.py` and `regenerate_npz_expanded.py`, `augment()` is `[pipeline(image=face)["image"] for _ in range(n)]`, so index 0 is also a random draw of the pipeline (flip p=0.5, brightness/contrast p=0.7, rotate +-15 p=0.5, Gaussian noise p=0.3). I found no clean crop in the npz.

Evidence from the npz: among the 30 variants of a source, 28.45 (old 20) and 28.50 (new 12) are distinct images on average, so about 1.5 variants per source are no-op draws. Only 57 old-20 sources and 30 new-12 sources have an aug0 identical to another variant. Val and test are therefore slightly noisy, randomly augmented images. The baseline had the same property, so this does not explain the gap. It does mean val and test accuracy include augmentation noise.

Val and test size in v1 (from the log): val 4 batches, test 4 batches (about 100 samples each, about 3 photos per class). One photo moves val acc by about 1%.

## 4. Crop channel order and resize versus the baseline

- Baseline and expanded npz use the same code for detect, crop, resize and augment. `detect_and_crop`, `build_aug_pipeline` and `augment` are identical in `regenerate_npz.py` and `regenerate_npz_expanded.py`. The expanded copy's only changes are `--dataset`, `--output` and a guard against overwriting the original npz (11-line diff, 10 insertions).
- Both store 160x160 RGB uint8 crops. The trainer resizes them identically to 112x112 with PIL bilinear and the same normalisation. Channel order and resize are the same for the 20 old and 12 new classes.
- The npz images array is (30390,160,160,3) uint8. Metadata keys: source_image, student_id, augmentation_index, original_bbox, det_score.
- `vista/vision/facial_pipeline.py` (`AUGMENTATION_CONFIG`, `build_augmentation_pipeline`) has the same four transforms and probabilities as the regenerate scripts. `TARGET_SIZE = (160,160)` and `AUGMENTATIONS_PER_FACE = 30`.

## 5. 30 augmentations per source photo and recipe of the 12 new students

Checked on `facial_pipeline_results_expanded.npz` (`part_e_check.py`):

| Check | Result |
|---|---|
| Total samples | 30,390 |
| Unique (student, source photo) pairs | 1,013 |
| Pairs whose `augmentation_index` set is exactly 0..29 | 1,013 of 1,013 (0 exceptions) |
| Classes with exactly 30 variants for every source | 32 of 32 |
| Sources per class | min 26, max 41 |
| Old 20 | 671 sources, 20,130 samples, mean det_score 0.8127 (min 0.5491) |
| New 12 | 342 sources, 10,260 samples, mean det_score 0.8302 (min 0.6907) |

Same recipe for the new 12: they were built by `regenerate_npz_expanded.py` in a single run over all 32 folders (`.agents/tasks/dataset-expansion/s4-npz.md`), with the same detector, crop, 160x160 resize, 4-transform pipeline and n=30 as the original 20. Notes in `s3-augment.md` show `augment_missing.py` did not process the 12 new students (it skipped them as not in roster, 0 files written for them), so the old `agumented data` folder was never involved. Hi-freq energy of aug0 vs other variants (old 8.78 vs 7.69, new 8.68 vs 8.65) shows no systematic recipe difference. Both groups also have a similar mean distinct-variant count (28.45 vs 28.50).

Caveat: the 12 new students have 26 to 31 photos each, the same range as the old 20 (27 to 41). The new group has 342 photos for 12 classes, so on average 28.5 per class versus 33.6 for the old group.

## 6. Findings

1. No code difference explains the v1 failure. Architecture, freezing, lr, scheduler, loss, augmentation, seed, patience, preprocessing and split logic are identical to the baseline.
2. The only real change is data: 20 to 32 classes, and 12 new classes whose photos may be harder or noisier. Parts B and D of this diagnosis cover the data side.
3. All 32 classes have exactly 30 variants for every source photo, and the new 12 used the same code path as the old 20.
4. The "aug_idx 0 = original" claim is false. Val and test images are randomly augmented, in both baseline and v1. This adds noise to every reported number.
5. Training choices that could be improved in v2 (not defects of v1 vs baseline): single lr for backbone and head, no label smoothing, no class weights, val set of about 100 images, so the best epoch is picked on noisy accuracy. In the baseline, the best epoch was 1 and in v1 also epoch 1 (val acc 0.7157, then 0.6373 at epoch 6), so early stopping works on a very noisy signal.
6. `train_from_npz.py` was not edited.
