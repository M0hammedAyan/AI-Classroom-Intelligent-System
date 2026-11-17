# Where to add the v3 face-classifier graphs in "Final report.docx"

Read-only investigation. The comparison graphs (`compare_*.png`) are omitted by request. Nothing was edited except this file.

## 0. Summary answer

- All classifier results live in **Chapter 7, Section 7.5.1 "ResNet-50 Classifier Results"**. That section currently describes the old 20-class Split B result (90.10%) and has **no graph**. All six v3 graphs belong here.
- **Recommendation:** use three figure numbers, one per graph type (curves, confusion matrix, per-class accuracy). Show **Split B (the live model) as the main figure** and put Split A in the table and text. If you want all six PNGs, place them as panel (a) Split A and (b) Split B inside the same three figure numbers, so the numbering does not change. Captions for both variants are in section 2.
- **Numbering consequence:** the report uses chapter-based numbering. The three new figures come before the existing Chapter 7 figures, so the existing ones shift: gallery-threshold Fig 7.1 becomes Fig 7.4, XGBoost confusion matrix Fig 7.2 becomes Fig 7.5, and the unnumbered processing-time chart becomes Fig 7.6 (optional). Those two numbered figures have their title **baked into the PNG**, so the title strip must be cropped in Word and replaced by a text caption (details in section 1.3).
- **No new table number is needed.** Rewrite the existing Table 7.3 as a three-column Split A vs Split B table (section 3). That avoids renumbering Tables 7.4 to 7.12.
- **Outdated passages to replace:** 9 places (section 4): 7.5.1 intro, Table 7.3, 7.5.1 closing paragraphs, Table 7.2 row 1, 7.5.2 lead sentence (clarify only), 7.10 bullet, 7.11 summary, 8.2 conclusion, 8.4.1.
- **Dataset and methodology text** goes in 7.4 (after Table 7.2) and as one sentence group in 4.6.5 (section 6).

## 1. Report structure and conventions (evidence)

Source: python-docx dump of `Final report.docx` (body order). All headings are `Normal`-style paragraphs with manual formatting, so use the heading text to find locations, not Word style navigation.

### 1.1 Chapters (relevant ones in bold)

1 Introduction · 2 Literature Review · 3 Requirement Engineering · 4 System Design and Methodology (4.6.5 Classifier Fallback) · 5 Project Planning (Table 5.4 risks, 5.8) · 6 Implementation (6.5.4 Personal Classifier Fallback) · **7 Testing and Results** · 8 Applications, Conclusion and Future Enhancements.

Chapter 7 outline: 7.1 Introduction, 7.2 Testing Strategy, 7.3 Functional Test Coverage (Table 7.1), **7.4 Evaluation Data and Conditions (Table 7.2)**, **7.5 Face Recognition Results** (**7.5.1 ResNet-50 Classifier Results**, Table 7.3; 7.5.2 Gallery Threshold Evaluation, Table 7.4, Fig 7.1; 7.5.3 Interpretation of Recognition Metrics; 7.5.4 Pilot Evidence), 7.6 Academic Risk Model Results (Tables 7.5 to 7.7, Fig 7.2), 7.7 Explainability (Table 7.8), 7.8 Processing-Time (Tables 7.9 to 7.11, unnumbered chart), 7.9 CIE/Study Coach (Table 7.12), **7.10 Limitations of Evaluation**, **7.11 Summary**.

### 1.2 Numbering and caption style

| Item | Scheme | Position | Example |
|---|---|---|---|
| Tables | `Table <chapter>.<n>`, plain text, no dash (Table 2.1 uses an en dash) | **Above** the table | "Table 7.3 ResNet-50 Classifier Results" |
| Figures, Chapter 6 | `Fig. <chapter>.<n> - Title`, plain text paragraph | **Below** the image | "Fig. 6.1 - Teacher Attendance Capture and Recognition Results" |
| Figures, Chapter 7 | Title **baked into the image** ("Fig. 7.1 - Effect of Cosine Similarity Threshold on Identification Accuracy and Rejection", "Fig. 7.2 - Confusion Matrix for XGBoost Academic Risk Classification"), no text caption | Above, inside the PNG | image20.png, image21.png |
| Third Ch 7 image | Processing-time line chart, **no number and no caption** (image22.png, end of 7.8.3) | n/a | |
| Chapters 4 and 5 figures | Embedded images with no text caption found | n/a | |

- The body text in Chapter 7 never refers to a figure by number (searched "Fig" and "Figure"), so renumbering does not break cross-references there. The only cross-reference found is in 7.5.3: "The counts in Table 7.4 ..." (unchanged if no new table is added).
- Total embedded images: 22 (word/media). **No image currently shows classifier graphs.** The old baseline curves and confusion matrices (`training_results/baseline_before_expansion/*.png`) are not in the report. The only classifier-related graph, Fig 7.1, is about gallery thresholds (ArcFace cosine), not the ResNet-50 classifier.

### 1.3 Consequence for the new figures

Because the Chapter 7 images carry baked-in titles, I recommend this for consistency and editability:
1. New v3 figures: insert as pictures with a **text caption below** in Chapter 6 style (`Fig. 7.x - ...`). The v3 PNG titles read "v3 Split B: ..." (internal label "v3"). Either crop the title off or accept it; cleaner is to regenerate with `training_results/expanded_v3/make_graphs_v3.py` without "v3" in the titles (not done here, read-only).
2. Existing Fig 7.1 and Fig 7.2: in Word select the picture, Picture Format > Crop, cut off the top title strip, and add a text caption below ("Fig. 7.4 - Effect of Cosine Similarity Threshold on Identification Accuracy and Rejection", "Fig. 7.5 - Confusion Matrix for XGBoost Academic Risk Classification"). The generator script for those two PNGs was not found in the repo (`git grep` returned nothing), so cropping is the practical route.
3. Processing-time chart: optionally add "Fig. 7.6 - Estimated Processing Time for Increasing Face Counts" below it.

## 2. The six graphs: what each shows, where it goes, caption, text

All numbers below were checked against `training_results/expanded_v3/eval_results.json`, `history_splitA.json`, `history_splitB.json`, `train_splitA.log`, `train_splitB.log`, `split_counts.csv`, `FIX_LOG.md`, `COMPARISON_REPORT.md`, `PROMOTION_LOG.md`.

### 2.0 Recommendation: B only, or A and B?

- **Curves:** B only in the main text. Split A's validation accuracy is 1.0000 at every epoch (95 validation photos), so its right-hand panel is a flat line that carries no model-selection information. Show A as panel (a) only if you want the tie to be visible; otherwise describe it in one sentence.
- **Confusion matrix:** B only. Both are near-perfect diagonals (29 x 29), large images (1430 x 1235 px). Two of them cost almost a page each and add little: A's two errors are described in text.
- **Per-class accuracy:** B only. A's bars differ in only two classes (2/3 each). Mention A in text.
- Reason: B is the live model (`PROMOTION_LOG.md`, `VISTA_FACE_MODEL` = `best_model_expanded_v3_splitB.pth`), it has the larger test set (138 vs 95), and the report already stresses concise evidence. Three figures instead of six saves about two pages.
- If you insist on all six: same three numbers, with panels (a) Split A and (b) Split B, and use the "A+B" captions below.

### 2.1 Fig 7.1 - Training curves (`v3_curves_splitB.png`, and optionally `v3_curves_splitA.png`)

- **Files:** `D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\training_results\expanded_v3\graphs\v3_curves_splitB.png` (main), `...\v3_curves_splitA.png` (optional panel a).
- **What B shows (viewed):** two panels, epochs 1 to 10 on the x axis. Left, loss (label-smoothed, class-weighted): train falls from 1.047 (epoch 1) to 0.660 (epoch 10); validation starts at 0.698, stays between 0.684 and 0.716 (peak 0.716 at epoch 6) and ends at 0.684. Right, accuracy: train 0.906 at epoch 1, 0.996 at epoch 2, 1.000 at epoch 10; validation 0.986, 0.986, 0.993, 0.978, 0.993, 0.971, 0.986, 0.978, 0.993, 0.993 (zig-zags within 0.971 to 0.993). A dashed vertical line marks the kept checkpoint at epoch 3 (validation 0.9928 = 137/138).
- **What A shows (viewed):** epochs 1 to 8. Train loss 1.028 to 0.664, validation loss 0.668 to 0.651 (below train from the start). Train accuracy 0.909 (epoch 1), 0.996 (epoch 2), 0.999 (epoch 8). Validation accuracy is a flat line at 1.000 for all 8 epochs. Dashed line at epoch 1 ("kept checkpoint (epoch 1)").
- **Insertion point:** Section 7.5.1, directly after Table 7.3 and the paragraph P3 that follows it (P3 in section 5 begins "Table 7.3 shows that the classifier correctly identified 93 of 95..."). Put the body text below, then the picture, then the caption.
- **Caption (B only):** `Fig. 7.1 - Training and Validation Loss and Accuracy of the ResNet-50 Classifier (Split B, 70:15:15, 29 Classes)`
- **Caption (A+B):** `Fig. 7.1 - Training and Validation Loss and Accuracy of the ResNet-50 Classifier: (a) Split A (80:10:10), (b) Split B (70:15:15)`
- **Body text (paste before the figure):**
  > Fig. 7.1 shows the training history of the Split B classifier. Training accuracy rises from 90.61% in the first epoch to 99.58% in the second and reaches 100.00% in the tenth epoch. Validation accuracy lies between 97.10% and 99.28% throughout. The checkpoint with the best validation accuracy, 99.28% (137 of 138 validation photographs), was reached at epoch 3 and kept; training stopped at epoch 10 under the patience-7 rule. Validation loss changes little after the first epoch, between 0.684 and 0.716.
  >
  > The loss values plateau near 0.66 because the loss uses label smoothing of 0.1, which prevents the loss from approaching zero even when every training sample is classified correctly; the plateau therefore does not indicate underfitting. For Split A, the validation accuracy was 100.00% (95 of 95 photographs) at every epoch, so the epoch-1 checkpoint was kept only because it was first, and the validation curve gave no information for choosing between epochs. Training for Split A stopped at epoch 8.

### 2.2 Fig 7.2 - Confusion matrices (`v3_confusion_splitB.png`, optionally `v3_confusion_splitA.png`)

- **Files:** `...\graphs\v3_confusion_splitB.png` (main), `...\graphs\v3_confusion_splitA.png` (optional).
- **What B shows (viewed):** 29 x 29 heat map, title "v3 Split B test confusion matrix (n=138, acc=0.9928)". True labels on the y axis, predicted on the x axis, USNs `1DA23AI001` to `1DA25AI010`. Every diagonal cell is filled (values 4 to 6, the number of test photos per class). The single off-diagonal cell is 1 at row `1DA24AI404`, column `1DA23AI031`; the diagonal cell for `1DA24AI404` is 3.
- **What A shows (viewed):** title "n=95, acc=0.9789". Diagonal values 3 or 4. Two off-diagonal cells: `1DA23AI024` to `1DA25AI008` (1; its diagonal is 2) and `1DA24AI404` to `1DA23AI050` (1; its diagonal is 2).
- **Insertion point:** Section 7.5.1, directly after Fig 7.1 and its caption, before Fig 7.3 (body text first, then picture, then caption).
- **Caption (B only):** `Fig. 7.2 - Test Confusion Matrix of the ResNet-50 Classifier (Split B, 138 Test Photographs, 29 Classes)`
- **Caption (A+B):** `Fig. 7.2 - Test Confusion Matrices of the ResNet-50 Classifier: (a) Split A (95 Test Photographs), (b) Split B (138 Test Photographs)`
- **Body text:**
  > Fig. 7.2 presents the confusion matrix for the Split B test set. Of the 138 test photographs, 137 lie on the diagonal. The only error is one photograph of student 1DA24AI404, which was assigned to 1DA23AI031. In Split A (95 test photographs), two photographs were misclassified: one of 1DA23AI024 was assigned to 1DA25AI008, and one of 1DA24AI404 was assigned to 1DA23AI050.
  >
  > The three errors across the two splits involve two students and three different predicted identities, and no pair of students is confused in both splits. Student 1DA24AI404 is misclassified in both splits, which suggests that this student's photographs are harder to separate, although a single error per split is too few to establish a cause. The matrix does not contain unknown faces, so it does not show how the classifier behaves for people who are not enrolled.

### 2.3 Fig 7.3 - Per-class accuracy (`v3_per_class_accuracy_splitB.png`, optionally `..._splitA.png`)

- **Files:** `...\graphs\v3_per_class_accuracy_splitB.png` (main), `...\graphs\v3_per_class_accuracy_splitA.png` (optional).
- **What B shows (viewed):** bar chart of test accuracy per student, y axis 0 to 1.1. Blue bars are the 19 original students, orange bars the 10 new students (`1DA25AI*`). Each bar is labelled with correct/total (4/4, 5/5, 6/6, ...). 28 of 29 bars reach 1.0; the one shorter bar is `1DA24AI404` at 3/4 (0.75). All 10 orange bars are 1.0.
- **What A shows (viewed):** same layout. 27 bars at 1.0; two blue bars at 2/3 (0.667): `1DA23AI024` and `1DA24AI404`. All orange bars are 3/3 or 4/4.
- **Insertion point:** Section 7.5.1, after the paragraph on the confusion matrix, before the closing interpretation paragraphs.
- **Caption (B only):** `Fig. 7.3 - Per-Student Test Accuracy of the ResNet-50 Classifier (Split B; Original 19 Students in Blue, New 10 Students in Orange)`
- **Caption (A+B):** `Fig. 7.3 - Per-Student Test Accuracy of the ResNet-50 Classifier: (a) Split A, (b) Split B (Original 19 Students in Blue, New 10 Students in Orange)`
- **Body text:**
  > Fig. 7.3 shows test accuracy for each of the 29 students. In Split B, 28 students are classified correctly on every test photograph; student 1DA24AI404 reaches 3 of 4 (75.00%). The 19 original students reach 98.94% (93 of 94 photographs, 95% Wilson interval 94.22% to 99.81%) and the 10 new students reach 100.00% (44 of 44, interval 91.97% to 100.00%). In Split A, 27 students are classified correctly on every photograph, and 1DA23AI024 and 1DA24AI404 each reach 2 of 3 (66.67%); the original 19 students reach 96.83% (61 of 63) and the new 10 reach 100.00% (32 of 32).
  >
  > Each student has only 3 to 4 (Split A) or 4 to 6 (Split B) test photographs, so a single photograph changes a student's accuracy by 17 to 33 percentage points. The per-student bars therefore describe the observed outcomes and do not provide a reliable estimate of individual error rates.

## 3. Results table (rewrite Table 7.3 in place, no new number)

**Location:** Section 7.5.1, replacing the existing "Table 7.3 ResNet-50 Classifier Results" (currently 2 columns, 11 rows: Metric / Recorded Value). Keep the caption above the table. Do not renumber Tables 7.4 to 7.12.

Table 7.3 ResNet-50 Classifier Results (29 Identity Classes)

| Metric | Split A (80:10:10) | Split B (70:15:15) |
|---|---|---|
| Number of identity classes | 29 | 29 |
| Source photographs (train / validation / test) | 740 / 95 / 95 | 654 / 138 / 138 |
| Training samples (clean crop + 30 augmentations per photograph) | 22,940 | 20,274 |
| Validation / test samples (clean crops) | 95 / 95 | 138 / 138 |
| Input image size | 112 × 112 pixels | 112 × 112 pixels |
| Epochs run (maximum 30) | 8 | 10 |
| Best epoch (checkpoint kept) | 1 | 3 |
| Best validation accuracy | 100.00% (every epoch) | 99.28% |
| Final training accuracy | 99.94% | 100.00% |
| Test accuracy | 97.89% (93 of 95) | 99.28% (137 of 138) |
| 95% confidence interval (Wilson) | 92.65% to 99.42% | 96.01% to 99.87% |
| Original 19 students, test accuracy | 96.83% (61 of 63) | 98.94% (93 of 94) |
| New 10 students, test accuracy | 100.00% (32 of 32) | 100.00% (44 of 44) |
| Test macro precision | 0.9845 | 0.9943 |
| Test macro recall | 0.9770 | 0.9914 |
| Test macro F1-score | 0.9774 | 0.9919 |

Check: A train 740 × 31 = 22,940, B 654 × 31 = 20,274, total 930 × 31 = 28,830 (`FIX_LOG.md`, `split_counts.csv`). Final training accuracy from `history_split*.json` (A 0.9994, B 1.0000). Source: `eval_results.json` keys `overall`, `original_19`, `new_10`, `macro_*`.

## 4. Outdated passages (quote, location, replacement)

The old numbers are the **earlier 20-class baseline** (`baseline_before_expansion/results_npz_split*.txt`: Split A 86.76% test, 68 test samples, 16,080 train samples, best val 88.06%; Split B 90.10%, 101 test samples, 14,070 train samples, best val 93.07%). The report cites only Split B. The string "86.76" does not appear in the report. Keep the baseline as history in one sentence; replace it where it describes the current system.

| # | Location | Current text (quoted) | Action |
|---|---|---|---|
| 4.1 | 7.5.1, first paragraph | "The recorded Split B classifier evaluation uses 20 student identity classes. The training record reports 14,070 augmented training samples, 101 unaugmented validation samples, and 101 unaugmented test samples." | Replace with the paragraph in section 5 (P1). |
| 4.2 | Table 7.3 | rows 20 / 14,070 / 101 / 101 / 8 epochs / 93.07% / 96.50% / 90.10% / 0.8846 | Replace with the table in section 3. Old values move to one baseline sentence (P6 in section 5). |
| 4.3 | 7.5.1, last two paragraphs | "The test accuracy corresponds to 91 correctly classified samples out of 101. However, performance differs across identities. One class has no correctly classified test samples ..." and "The overall result therefore demonstrates classifier feasibility on the evaluated data but does not establish equal reliability for every student." | Replace with P5 and P6 in section 5. The "no correctly classified test samples" statement is no longer true for v3. |
| 4.4 | Table 7.2 row 1 | "Face classifier evaluation \| 101 unaugmented test samples across 20 identities \| Evaluate ResNet-50 identity classification" | Replace with: "Face classifier evaluation \| 95 (Split A) and 138 (Split B) clean test crops across 29 identities \| Evaluate ResNet-50 identity classification". |
| 4.5 | 7.5.2 first sentence; Table 7.2 row 2; Fig 7.1 subtitle "107 test samples across 20 gallery classes" | "The gallery matching evaluation compares several cosine similarity thresholds." | **Keep the data.** It is a separate earlier ArcFace gallery experiment and was not re-run. Add after the sentence: "This threshold evaluation was recorded earlier on a 20-student gallery and was not repeated for the expanded 29-student dataset." |
| 4.6 | 7.10, first bullet | "Recognition datasets contain relatively few original test samples per identity." | Replace with: "Recognition test sets are small: 3 to 4 photographs per student in Split A and 4 to 6 in Split B, so a single photograph changes a student's accuracy by 17 to 33 percentage points." Add the other bullets in section 7. |
| 4.7 | 7.11, first sentence | "The recorded face-classifier evaluation reports 90.10% accuracy across 101 test samples and 20 identities." | Replace with: "The recorded face-classifier evaluation on 29 identities reports 99.28% test accuracy (137 of 138 photographs) for Split B and 97.89% (93 of 95) for Split A, measured on clean single-face crops of a small test set; these values are not comparable with the earlier 20-class result of 90.10%." |
| 4.8 | 8.2, sentence in paragraph "The recorded evaluation demonstrates useful capabilities..." | "The ResNet classifier achieved 90.10% test accuracy on a limited dataset containing 20 identities." | Replace with: "The ResNet classifier trained on 29 identities achieved 99.28% test accuracy (137 of 138 clean test crops) for the 70:15:15 split now used by the application and 97.89% (93 of 95) for the 80:10:10 split, on a small closed-set test; an earlier 20-class classifier reached 90.10%, but the two results use different class sets and test crops and are not directly comparable." |
| 4.9 | 8.4.1 | "The recorded classifier evaluation covers a restricted set of identities. It does not establish recognition performance across different classrooms, cameras, lighting conditions, seating arrangements, and student populations." | Keep, and append: "The test sets contain 95 and 138 clean single-face crops of 29 enrolled students, with no unknown faces, multi-face scenes, or classroom-condition variation." |

Not outdated (verified): 3.6.2, 4.6.5, 6.5.4 (runtime 112 × 112 normalisation and the 0.60 default threshold match `PROMOTION_LOG.md`: `VISTA_FACE_MODEL_THRESHOLD=0.60`); Table 7.10 classifier timing (architecture unchanged; only the head width changed from 20 to 29); Table 5.4 risk row "Leakage between training and test data" (the mitigation "Split data by original source image before augmentation" is exactly what v3 does; optionally append "validated by comparing file hashes across splits").

## 5. Ready-to-paste replacement text for Section 7.5.1 (in order)

Heading "7.5.1 ResNet-50 Classifier Results" stays. New order: P1, P2, Table 7.3, P3, Fig 7.1 + caption, P4, Fig 7.2 + caption, Fig 7.3 + caption, P5, P6. (Fig paragraphs are in section 2; they replace the placeholders.)

**P1 (replaces the first paragraph, "The recorded Split B classifier evaluation uses..."):**
> The recorded classifier evaluation uses an expanded dataset of 29 student identities: 19 originally enrolled students and 10 additional students (1DA25AI001 to 1DA25AI010). After 17 photographs showing a wrong face or no detectable face were excluded, the dataset contained 930 source photographs. Each photograph contributes one clean face crop and 30 augmented variants, giving 28,830 samples. Two splits were evaluated by source photograph: Split A (80:10:10) with 740 training, 95 validation, and 95 test photographs, and Split B (70:15:15) with 654, 138, and 138 photographs. The training sets contain 22,940 and 20,274 samples respectively. Validation and test sets contain only clean, unaugmented crops, one per photograph, and no photograph appears on more than one side of a split.

**P2 (new, after P1):**
> Each split used a freshly initialised ImageNet-pretrained ResNet-50 with a new 29-way output layer, 112 × 112 pixel input, normalisation with mean 0.5 and standard deviation 0.5, the Adam optimiser with a learning rate of 1e-4, label smoothing of 0.1, class-weighted cross-entropy loss, early stopping with a patience of 7 epochs, a maximum of 30 epochs, and a random seed of 42. Training ran on an NVIDIA RTX 3050 laptop GPU. The Split B checkpoint is the one used by the application.

[Table 7.3 here]

**P3 (after Table 7.3, before Fig 7.1):**
> Table 7.3 shows that the classifier correctly identified 93 of 95 test photographs in Split A (97.89%) and 137 of 138 in Split B (99.28%). The 95% Wilson confidence intervals are 92.65% to 99.42% and 96.01% to 99.87%. The ten new students were identified correctly in every test photograph in both splits (32 of 32 and 44 of 44), and the original 19 students reached 96.83% and 98.94%. Test macro F1-scores are 0.9774 and 0.9919.

[Fig 7.1 paragraph, image, caption]

**P4 (before Fig 7.2):** use the first paragraph of section 2.2. Then the Fig 7.2 and Fig 7.3 blocks from sections 2.2 and 2.3.

**P5 (replaces "The test accuracy corresponds to 91 ..."):**
> Performance is high across identities: 28 of 29 students in Split B and 27 of 29 in Split A are classified correctly on every test photograph. The remaining errors occur among the original students, and none occurs for the new students. These results show that the classifier can separate the 29 enrolled identities in this dataset; they do not show how it performs on photographs taken under classroom conditions.

**P6 (replaces "The overall result therefore demonstrates..." and keeps the baseline as history):**
> An earlier classifier trained on 20 identities reached 90.10% test accuracy in the 70:15:15 split (91 of 101 test samples) and 86.76% in the 80:10:10 split (68 test samples). These values are not directly comparable with Table 7.3, because the class sets differ (20 against 29 identities), the test photographs differ, and the earlier test samples were randomly augmented while the present ones are clean crops. The earlier result is retained only as a record of the previous recorded experiment. The earlier low accuracy of an intermediate 32-class attempt (best validation accuracy 71.57% and 67.76%) was traced to duplicate photographs stored under two student labels, as described in Section 7.4.

(Check: 71.57% and 67.76% from `COMPARISON_REPORT.md`. If you prefer not to mention the failed intermediate run, delete the last sentence of P6.)

## 6. Dataset and methodology update

Yes, an update is needed. The report currently says nothing about how the classifier dataset was built (only generic "dataset organization" in 5.5.1, "Split data by original source image before augmentation" in Table 5.4, and "uses real photographs" in 6.12.1/7.10).

**6.1 Location A: Section 7.4 "Evaluation Data and Conditions"**, new paragraphs after the sentence beginning "These evaluations should not be combined into a single system accuracy figure" (the one following Table 7.2).

> The face-classifier dataset was rebuilt and re-audited before the recorded evaluation. An earlier attempt on 32 identities reached only 71.57% and 67.76% best validation accuracy because several folders held the same photographs under two different student labels: six such pairs among the twelve then-new students and one pair among the original twenty, with byte-identical files and mean ArcFace cosine similarity of 0.9993 to 0.9998. Identical faces under different labels cannot be separated by any classifier, and the duplicates also leaked across training and evaluation data.
>
> After the duplicates were resolved, the audit of the final 29 student folders (947 photographs) found no duplicate files, no photograph stored under two labels, and no pair of students with an embedding cosine similarity above 0.6 (highest 0.4104). One student whose photographs had been removed (1DA22AI402) is not included, and 17 photographs showing a wrong face or no detectable face were excluded, leaving 930 photographs. Each photograph yields one clean face crop and 30 augmented variants (horizontal flip, brightness and contrast change, rotation up to 15 degrees, and noise). Validation and test sets use only the clean crops, with at least three validation and three test photographs per student, and the split is made by source photograph so that no photograph or file content appears in more than one set. For the 19 earlier students the augmented variants were reused from the previous dataset.

(Sources: `COMPARISON_REPORT.md` "What was wrong in v1", `FIX_LOG.md` part 2, `diagnosis/AUDIT_V3.md`: 29 folders, 947 photos.)

**6.2 Location B: Section 4.6.5 "Classifier Fallback"**, after the paragraph ending "The classifier can identify only the classes represented in its trained artifact." Add:

> The classifier currently covers 29 enrolled identities. It was trained from ImageNet-pretrained ResNet-50 weights with label smoothing and class-weighted loss, and the 70:15:15 split checkpoint is loaded by the application with an acceptance threshold of 0.60. A check on 223 correct held-out predictions showed that this threshold would reject 2 of them (0.9%) and rejected all wrong predictions, whose highest confidence was 0.326.

(Source: `PROMOTION_LOG.md` Step 3. The 223 is 138 clean crops plus 87 raw photos, both Split B test photographs. Remove this paragraph if you prefer not to add the threshold evidence.)

## 7. Honesty points and where each belongs

| Point | Primary location | Also |
|---|---|---|
| Small test sets, wide CIs (95 and 138 photos; 3 to 6 per student; one photo moves a student by 17 to 33 points) | 7.5.1 P3 and Fig 7.3 text (already written above); replacement 7.10 bullet | 8.4.1 |
| Clean single-face crops only (test crops are unaugmented, centred face crops, not classroom photographs) | 7.10 new bullet (below); 7.4 paragraph | 8.4.1 |
| Closed set, no unknown faces; unknown-face rejection not verified | 7.10 new bullet; Fig 7.2 text already says so | 8.4.1; `PROMOTION_LOG.md`: the five photos of the removed student 1DA22AI402 were all predicted as 1DA24AI403 at 0.89 to 0.93 confidence, and no real unknown-person photos exist in the repository |
| Split A validation tie (100% every epoch; epoch-1 checkpoint kept because it came first; no selection signal) | Fig 7.1 text (already written above) | 7.10 bullet |
| 20-class vs 29-class not directly comparable | 7.5.1 P6; 7.11; 8.2 (already written) | |
| Test accuracy and macro F1 are on the held-out split, not tuned on test; checkpoint chosen on validation only | 7.5.1 P2 (add "Checkpoints were selected on validation accuracy only; the test set was not used for tuning.") | |
| Model overconfidence on arbitrary input (one random-noise image reached 0.77 and would pass 0.60) | 7.10 new bullet, or omit | `PROMOTION_LOG.md`; face detection upstream guards it |

**New bullets for 7.10 "Limitations of Evaluation"** (replace bullet 1 as in 4.6, add these after it):
> - The classifier test sets contain clean, single-face crops of enrolled students. They do not include unknown or non-enrolled faces, small back-row faces, occlusion, or multi-face classroom scenes, and the task is closed-set. A 100% result for the ten new students therefore does not indicate classroom accuracy, and the lower bound of its confidence interval is 89.28% (Split A) and 91.97% (Split B).
> - The ability of the classifier to reject unknown faces has not been verified. The only non-student photographs available (five photographs of a student not in the 29 classes) were classified as an enrolled student with high confidence, and the 0.60 threshold cannot reject such cases.
> - In Split A, validation accuracy was 100% at every epoch, so the validation set gave no basis for choosing a checkpoint.
> - The 20-class and 29-class classifier results use different class sets and test crops and are not directly comparable.

## 8. Insertion-point summary (one place to look)

1. 7.4, after "These evaluations should not be combined into a single system accuracy figure": dataset paragraphs (6.1).
2. 4.6.5, after "The classifier can identify only the classes represented in its trained artifact.": coverage and threshold paragraph (6.2).
3. Table 7.2 row 1: replace (4.4).
4. 7.5.1: P1, P2, Table 7.3 (rewrite), P3, Fig 7.1, P4 (Fig 7.2 text), Fig 7.2, Fig 7.3 and text, P5, P6.
5. 7.5.2: add one sentence after "The gallery matching evaluation compares several cosine similarity thresholds." (4.5). Renumber the gallery chart to Fig 7.4 (caption below after cropping the baked title), the XGBoost matrix in 7.6.4 to Fig 7.5, and optionally caption the 7.8.3 chart as Fig 7.6.
6. 7.10: replace bullet 1, add three bullets (section 7).
7. 7.11 first sentence (4.7); 8.2 sentence (4.8); 8.4.1 appended sentence (4.9).

## 9. Caveats and open points

- Choosing "A and B both" vs "B only" is a length decision; it does not change numbering (section 2.0).
- The v3 PNG titles contain the internal label "v3" and "label-smoothed, class-weighted"; regenerate or crop before pasting (section 1.3). I did not modify the images.
- The report uses USNs (e.g. 1DA24AI404) for students. If the department prefers anonymity in the printed report, replace them with "Student A/B/C" in the Fig 7.2 and 7.3 text.
- Gallery experiments (Table 7.4, former Fig 7.1) and the 107-sample / 20-class numbers remain as recorded history. They were not re-run on 29 classes.
- Word cannot be edited from here; every insertion is by quoted text, not by paragraph number. The dump file indices I used while reading are body-element indices, not Word paragraph numbers.
