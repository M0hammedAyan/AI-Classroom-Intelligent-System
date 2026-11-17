# Final report inputs (29-student classifier): anonymised

All numbers below were recomputed from the checkpoints, `eval_results.json`, history files, split files and the npz, or read from the named file. Student IDs S01 to S29 follow one fixed mapping used by every graph and table (kept privately, not listed here).

## 1. Graphs (`training_results/expanded_v3/graphs_report/`)

Six PNGs, 300 dpi, opaque white background, no USNs and no internal labels: `curves_splitA.png`, `curves_splitB.png`, `confusion_splitA.png`, `confusion_splitB.png`, `per_student_accuracy_splitA.png`, `per_student_accuracy_splitB.png`. Script: `training_results/expanded_v3/make_report_graphs.py`. The script re-ran both checkpoints on the test clean crops and asserted that the confusion matrices, per-student correct/total counts and overall accuracy equal `eval_results.json` (all matched: 93/95 and 137/138). Each PNG was viewed and checked for legibility.

| File | Pixels | Title text |
|---|---|---|
| curves_splitA.png | 1890 x 900 | Training and Validation Loss and Accuracy (Split A, 80:10:10) |
| curves_splitB.png | 1890 x 900 | Training and Validation Loss and Accuracy (Split B, 70:15:15) |
| confusion_splitA.png | 1950 x 1800 | Test Confusion Matrix (Split A, 95 test photographs) |
| confusion_splitB.png | 1950 x 1800 | Test Confusion Matrix (Split B, 138 test photographs) |
| per_student_accuracy_splitA.png | 1890 x 1020 | Per-Student Test Accuracy (Split A, 80:10:10) |
| per_student_accuracy_splitB.png | 1890 x 1020 | Per-Student Test Accuracy (Split B, 70:15:15) |

Curves: loss axis is labelled "Loss (with label smoothing 0.1)"; the kept checkpoint is a dashed vertical line ("Selected checkpoint (epoch 1)" for A, "(epoch 3)" for B). Per-student charts: one bar colour, dashed line at overall test accuracy (97.89% for A, 99.28% for B). Confusion matrices: all 29 labels on both axes, every non-zero cell annotated.

## 2. Gallery threshold experiment (Table 7.4)

### 2.1 What the report's Table 7.4 contains

Caption: `Table 7.4 Selected Gallery Matching Results`. Paragraph after the table: `Each row contains 107 evaluated samples.` Section 7.5.2 starts: `The gallery matching evaluation compares several cosine similarity thresholds.` Table 7.2 row 2 reads: `Gallery threshold sweep | 107 test samples and 20 gallery classes | Examine cosine-threshold behavior`.

| Threshold | Correct Matches | Wrong-Identity Matches | Rejected Samples | Identification Accuracy |
|---|---|---|---|---|
| 0.30 | 92 | 12 | 3 | 85.98% |
| 0.40 | 89 | 9 | 9 | 83.18% |
| 0.55 | 84 | 8 | 15 | 78.50% |
| 0.70 | 57 | 5 | 45 | 53.27% |
| 0.80 | 20 | 0 | 87 | 18.69% |

### 2.2 What produced it

`evaluation/evaluate_recognition.py` wrote `evaluation/results/recognition_threshold_sweep.json`, which records dataset `facial_pipeline_results.npz` (the earlier npz, not the 29-student file), **20 gallery classes and 107 test samples**. So it was NOT run on the 29-student data. Its gallery was the mean of about 70% of the unaugmented crops, chosen by a hash of the source-image name (Python string hashing, which varies between runs) or, if fewer than 50 test crops resulted, by a seeded random 70/30 split; the split is therefore not reproducible from the script alone. Thresholds were 0.30 to 0.80 in steps of 0.05. Table 7.4 shows five of them (0.30, 0.40, 0.55, 0.70, 0.80); its "Identification Accuracy" column is correct/107.

### 2.3 Re-run on the 29-student data (Split B)

Script: `evaluation/evaluate_gallery_29class.py`. Results: `evaluation/results/gallery_threshold_29class_splitB.json`.

- Students (gallery classes): **29**. Probe samples: **138** (Split B test clean crops, one per test photograph).
- Gallery: per-student mean of the L2-normalised ArcFace embeddings of the clean crops of that student's Split B training photos only (654 photographs), re-normalised. Database embeddings were not used, so no test photograph is in the gallery.
- Each probe is matched to its top-1 prototype by cosine similarity; it is accepted if that similarity is at or above the threshold.
- Definitions: accepted correct = top-1 is the true student and similarity >= threshold; accepted wrong identity = top-1 is another student and similarity >= threshold; rejected = top-1 similarity < threshold; precision = correct / (correct + wrong); recall = correct / 138 (all probes, equal to identification accuracy); F1 = 2PR/(P+R).
- The original script defines recall differently: correct / (correct + rejected), which leaves wrong-identity accepts out of the denominator. That variant is given in the last two columns so the two definitions can be told apart.

| Threshold | Accepted correct | Accepted wrong identity | Rejected | Precision | Recall (correct/138) | F1 | Recall, original definition | F1, original definition |
|---|---|---|---|---|---|---|---|---|
| 0.20 | 133 | 5 | 0 | 0.9638 | 0.9638 | 0.9638 | 1.0000 | 0.9815 |
| 0.25 | 133 | 5 | 0 | 0.9638 | 0.9638 | 0.9638 | 1.0000 | 0.9815 |
| 0.30 | 131 | 5 | 2 | 0.9632 | 0.9493 | 0.9562 | 0.9850 | 0.9740 |
| 0.35 | 131 | 3 | 4 | 0.9776 | 0.9493 | 0.9632 | 0.9704 | 0.9740 |
| 0.40 | 130 | 2 | 6 | 0.9848 | 0.9420 | 0.9630 | 0.9559 | 0.9701 |
| 0.45 | 129 | 1 | 8 | 0.9923 | 0.9348 | 0.9627 | 0.9416 | 0.9663 |
| 0.50 | 128 | 0 | 10 | 1.0000 | 0.9275 | 0.9624 | 0.9275 | 0.9624 |
| 0.55 | 125 | 0 | 13 | 1.0000 | 0.9058 | 0.9506 | 0.9058 | 0.9506 |
| 0.60 | 123 | 0 | 15 | 1.0000 | 0.8913 | 0.9425 | 0.8913 | 0.9425 |
| 0.65 | 118 | 0 | 20 | 1.0000 | 0.8551 | 0.9219 | 0.8551 | 0.9219 |
| 0.70 | 105 | 0 | 33 | 1.0000 | 0.7609 | 0.8642 | 0.7609 | 0.8642 |
| 0.80 | 67 | 0 | 71 | 1.0000 | 0.4855 | 0.6537 | 0.4855 | 0.6537 |

- Best F1 (recall = correct/138): **0.9638** at thresholds **0.20, 0.25** (tie: the two thresholds give identical counts, 133 correct, 5 wrong identity, 0 rejected). With the original recall definition the best F1 is 0.9815 at the same thresholds.
- At the application threshold 0.55: 125 correct, 0 wrong identity, 13 rejected out of 138; precision 1.0000, recall 0.9058, F1 0.9506.
- Without any threshold, top-1 is correct for 133 of 138 probes. The 5 wrong top-1 matches have similarities 0.309, 0.328, 0.350, 0.402, 0.469; the lowest similarity of a correct match is 0.263.
- The threshold trades recall for precision: raising it from 0.20 to 0.50 removes all 5 wrong-identity accepts, and by 0.50 precision is 1.0000 while 10 probes are rejected. This is a different experiment from Table 7.4 (different gallery source, 29 instead of 20 students, 138 instead of 107 probes), and the numbers are not meant to be merged into that table row by row.

## 3. Verbatim report text

### 3.1 Table 7.2 (Evaluation Scope), row 1 (first data row, all cells; header row is `Evaluation | Data or Workload | Purpose`)

```
'Face classifier evaluation'
'101 unaugmented test samples across 20 identities'
'Evaluate ResNet-50 identity classification'
```

### 3.2 Full current Table 7.3

Caption: `Table 7.3 ResNet-50 Classifier Results`

| Metric | Recorded Value |
|---|---|
| Number of identity classes | 20 |
| Training samples | 14,070 |
| Validation samples | 101 |
| Test samples | 101 |
| Input image size | 112 × 112 pixels |
| Epochs completed | 8 |
| Best validation accuracy | 93.07% |
| Final training accuracy | 96.50% |
| Test accuracy | 90.10% |
| Test macro F1-score | 0.8846 |

(These are the current 20-class values in the report, pasted verbatim as requested.)

## 4. Misclassified test photographs and test counts

### Split A (95 test photographs)

Confidence is the softmax probability of the predicted class, from the checkpoint run on the test clean crops (RGB, resize 112 x 112 bilinear, ToTensor, normalise mean 0.5 std 0.5, as in `train_expanded_v3.py`). Accuracy reproduced: 93/95, equal to `eval_results.json`.

| True ID | Predicted ID | Predicted confidence |
|---|---|---|
| S06 | S27 | 0.2708 |
| S19 | S15 | 0.1170 |

### Split B (138 test photographs)

Confidence is the softmax probability of the predicted class, from the checkpoint run on the test clean crops (RGB, resize 112 x 112 bilinear, ToTensor, normalise mean 0.5 std 0.5, as in `train_expanded_v3.py`). Accuracy reproduced: 137/138, equal to `eval_results.json`.

| True ID | Predicted ID | Predicted confidence |
|---|---|---|
| S19 | S08 | 0.3253 |

### Test photographs per student

| ID | Split A test | Split B test |
|---|---|---|
| S01 | 4 | 6 |
| S02 | 3 | 4 |
| S03 | 4 | 6 |
| S04 | 3 | 5 |
| S05 | 3 | 4 |
| S06 | 3 | 4 |
| S07 | 4 | 6 |
| S08 | 3 | 5 |
| S09 | 4 | 6 |
| S10 | 3 | 4 |
| S11 | 3 | 5 |
| S12 | 4 | 6 |
| S13 | 4 | 5 |
| S14 | 3 | 5 |
| S15 | 3 | 4 |
| S16 | 3 | 5 |
| S17 | 3 | 5 |
| S18 | 3 | 5 |
| S19 | 3 | 4 |
| S20 | 3 | 5 |
| S21 | 3 | 4 |
| S22 | 3 | 4 |
| S23 | 3 | 4 |
| S24 | 3 | 4 |
| S25 | 3 | 4 |
| S26 | 3 | 5 |
| S27 | 4 | 5 |
| S28 | 4 | 5 |
| S29 | 3 | 4 |
| Total | 95 | 138 |

## 5. Per-epoch training history and source photographs

### Split A (`graphs_report/epochs_splitA.csv`)

| epoch | train_loss | train_acc | val_loss | val_acc |
|---|---|---|---|---|
| 1 | 1.0279 | 0.9089 | 0.6676 | 1.0000 |
| 2 | 0.6930 | 0.9964 | 0.6593 | 1.0000 |
| 3 | 0.6799 | 0.9972 | 0.6607 | 1.0000 |
| 4 | 0.6763 | 0.9980 | 0.6594 | 1.0000 |
| 5 | 0.6779 | 0.9967 | 0.6508 | 1.0000 |
| 6 | 0.6690 | 0.9988 | 0.6510 | 1.0000 |
| 7 | 0.6659 | 0.9991 | 0.6493 | 1.0000 |
| 8 | 0.6637 | 0.9994 | 0.6506 | 1.0000 |

### Split B (`graphs_report/epochs_splitB.csv`)

| epoch | train_loss | train_acc | val_loss | val_acc |
|---|---|---|---|---|
| 1 | 1.0469 | 0.9061 | 0.6984 | 0.9855 |
| 2 | 0.6954 | 0.9958 | 0.6924 | 0.9855 |
| 3 | 0.6800 | 0.9977 | 0.6893 | 0.9928 |
| 4 | 0.6757 | 0.9977 | 0.6857 | 0.9783 |
| 5 | 0.6759 | 0.9972 | 0.6938 | 0.9928 |
| 6 | 0.6731 | 0.9975 | 0.7157 | 0.9710 |
| 7 | 0.6696 | 0.9983 | 0.7127 | 0.9855 |
| 8 | 0.6705 | 0.9981 | 0.7119 | 0.9783 |
| 9 | 0.6615 | 0.9996 | 0.6850 | 0.9928 |
| 10 | 0.6597 | 1.0000 | 0.6837 | 0.9928 |

Cross-check against `train_split*.log`: Split A: 8 log epochs, all values match history within log rounding (4 dp); Split B: 10 log epochs, all values match history within log rounding (4 dp).

Source photographs per student: used (930) min 25, max 41, median 32; audited (947) min 26, max 41, median 33.

| ID | Audited photographs | Excluded | Used photographs |
|---|---|---|---|
| S01 | 39 | 0 | 39 |
| S02 | 29 | 0 | 29 |
| S03 | 39 | 0 | 39 |
| S04 | 35 | 2 | 33 |
| S05 | 27 | 0 | 27 |
| S06 | 29 | 2 | 27 |
| S07 | 38 | 1 | 37 |
| S08 | 34 | 0 | 34 |
| S09 | 41 | 0 | 41 |
| S10 | 28 | 0 | 28 |
| S11 | 33 | 0 | 33 |
| S12 | 38 | 1 | 37 |
| S13 | 36 | 0 | 36 |
| S14 | 33 | 0 | 33 |
| S15 | 30 | 0 | 30 |
| S16 | 36 | 2 | 34 |
| S17 | 32 | 1 | 31 |
| S18 | 33 | 0 | 33 |
| S19 | 30 | 0 | 30 |
| S20 | 31 | 0 | 31 |
| S21 | 28 | 1 | 27 |
| S22 | 30 | 0 | 30 |
| S23 | 26 | 0 | 26 |
| S24 | 30 | 0 | 30 |
| S25 | 27 | 0 | 27 |
| S26 | 34 | 2 | 32 |
| S27 | 36 | 0 | 36 |
| S28 | 36 | 1 | 35 |
| S29 | 29 | 4 | 25 |
| Total | 947 | 17 | 930 |

## 6. Verification of the headline numbers

| Item | Status | Value found | Source |
|---|---|---|---|
| 29 classes | CONFIRMED | npz has 29 labels; both checkpoints have 29 classes | npz labels, splits_*.json |
| 947 photos audited | CONFIRMED | sum of per-student photo counts = 947 | diagnosis/students.csv (AUDIT_V3.md: 947) |
| 17 excluded | CONFIRMED | 947 - 930 = 17 | students.csv minus split_counts.csv |
| 930 used | CONFIRMED | sum of photos_total = 930 | split_counts.csv |
| 28,830 samples | CONFIRMED | npz has 28830 samples (930 x 31) | npz |
| Split A 740/95/95 photos | CONFIRMED | (740, 95, 95) | splits_A.json |
| Split B 654/138/138 photos | CONFIRMED | (654, 138, 138) | splits_B.json |
| Test accuracy A 97.89% (93/95) | CONFIRMED | 93/95 = 97.89% | eval_results.json; recomputed from checkpoint |
| Wilson 95% CI A 92.65-99.42% | CONFIRMED | recomputed 92.65-99.42% | Wilson score formula, z = 1.959964 |
| Macro F1 A 0.9774 | CONFIRMED | recomputed 0.9774 (eval_results.json: 0.9774) | from confusion matrix |
| Test accuracy B 99.28% (137/138) | CONFIRMED | 137/138 = 99.28% | eval_results.json; recomputed from checkpoint |
| Wilson 95% CI B 96.01-99.87% | CONFIRMED | recomputed 96.01-99.87% | Wilson score formula, z = 1.959964 |
| Macro F1 B 0.9919 | CONFIRMED | recomputed 0.9919 (eval_results.json: 0.9919) | from confusion matrix |

Additional values used in earlier text: Split A kept checkpoint epoch 1 (validation 100% at every epoch), Split B kept checkpoint epoch 3 (validation 99.28%); training stopped at epoch 8 (A) and 10 (B).

## 7. The five "non-enrolled person" photographs

Source: the photographs come from the dataset folder of a student who is no longer a class. That folder is deleted from the working tree but is still in git history; `threshold_check.py` drew a random sample of 5 of its photographs (it does not test the whole folder). `check_unenrolled_photos.py` re-ran all of them with the Split B checkpoint (face detection, crop, classifier, as the application does).

- The folder holds 34 photographs, not 5. The earlier test used a random sample of 5.
- Re-run on the 5 sampled photographs: all 5 had a detected face and were all predicted as the same enrolled student, with confidence **0.89 to 0.93** (exact 0.8945 to 0.9261). This matches the 0.89 to 0.93 recorded in `PROMOTION_LOG.md`. All 5 are at or above the 0.60 application threshold.
- Re-run on all 34 photographs: all face-detected, all predicted as that same enrolled student, confidence 0.8652 to 0.9304.
- Identity check: 33 of 34 photographs are byte-identical (same MD5) to photographs stored under one enrolled student; all 5 sampled ones are. ArcFace cosine to the nearest photograph of that enrolled student is 1.0000 to 1.0000 for the 5 sampled photographs (and 0.905 to 1.000 over all 34). The earlier audits (`diagnosis/DIAGNOSIS.md`, `AUDIT_V3.md`) recorded a class-mean cosine of 0.999.
- **Conclusion: these photographs show an enrolled student (the same photographs stored under a second folder), not a genuinely non-enrolled person. They are not a valid unknown-face test, and the report must not describe them as one.**
- Genuinely non-enrolled face photographs in the repository: **0**. The 29 dataset folders contain only enrolled students, the extra folder above duplicates one of them, and the remaining non-student inputs in the earlier check were non-face images (interface screenshots, a background patch, flat grey, random noise), whose confidences were 0.09 to 0.20, except random noise at 0.77. Unknown-face rejection therefore has not been tested.
