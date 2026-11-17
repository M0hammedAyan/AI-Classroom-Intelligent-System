# Edit plan for `3Report (1).docx`

Input (untouched): `1report\3Report (1).docx`. Backup copy: `1report\3Report (1)_original_backup.docx`. Output to write: `1report\3Report (1)_updated.docx`.
Analysis helpers in `1report\`: `dump_docx.py`, `_dump.txt` (full body dump, element index `[n]` = position in `document.body`), `fmt_probe.py`, `_fmt.txt`, `_x\` (unzipped docx). Delete `_x`, `_dump.txt`, `_fmt.txt` after the edit if not wanted.
Indices `[n]` below refer to body children in `_dump.txt` (tables count as one child). Re-find by the quoted text, not the index, once edits start shifting positions.

## 1. Real structure (differs from the earlier "Final report")

- Body starts at "Chapter 1" and ends with the references table (`[1197]`, 27x1). There is **no title page, TOC, List of Figures or List of Tables** in this file (no TOC/PAGEREF fields, no `w:sdt`, only a header/footer). So nothing to update there. Say so in the final report; do not create them.
- No separate Table/Figure fields: all captions are plain typed text (no SEQ fields). Numbering must be edited by hand.
- Evaluation chapter is Chapter 7. Relevant sections:
  - 7.4 Evaluation Data and Conditions, Table 7.2 `[972-973]`
  - 7.5.1 ResNet-50 Classifier Results `[978-985]`, Table 7.3 `[981-982]`
  - 7.5.2 Gallery Threshold Evaluation `[986-997]`, Table 7.4 `[989-990]`, figure `[996]` (image20.png)
  - 7.5.3 Interpretation of Recognition Metrics `[998-1002]`
  - 7.5.4 Pilot Evidence `[1003-1005]` (out of scope, leave)
  - 7.6 Academic Risk Model Results `[1007-1036]`, Tables 7.5 `[1013-1014]`, 7.6 `[1019-1020]`, 7.7 `[1025-1026]`, figure `[1030]` (image21.png)
  - 7.10 Limitations `[1089-1100]`, 7.11 Summary `[1102-1105]`
  - Chapter 8.2 Conclusion `[1132-1133]` repeats the numbers.
- Tables 7.8 to 7.12 and image22.png (processing-time chart, no number, no caption, out of scope) stay unchanged.

## 2. Caption and format conventions (copy exactly)

- Page: A4, margins 1134 twips (2 cm). Usable width = 6,120,130 EMU (17.0 cm). Full-width figures use cx=6120130 (cy by aspect ratio).
- Body text: Times New Roman 12 pt (`w:sz 24`), justified, `spacing line=259 auto`. Section headings: 16 pt bold (7.x), 14 pt bold (7.x.y), TNR, style Normal, no numbering fields.
- **Table captions: above the table**, centered, TNR 12 bold, text like `Table 7.3 ResNet-50 Classifier Results` (no dash, no colon, no trailing period). Caption paragraph pPr: `spacing line=259 auto`, `jc center`.
- Tables: style `Grid Table 1 Light`, `tblW auto`, table `jc center`, row `jc center`, cells `tcW auto`; cell paragraphs TNR 12, `spacing after=160 line=259 auto`, `jc both`; header row has `firstRow` cnfStyle (bold from style). An empty justified paragraph follows each table. To add rows/columns, deep-copy an existing row/cell XML (Table 7.4 for the gallery table) so the formatting matches.
- **Figure captions: below the figure**, centered, TNR 12 bold, text `Fig. 6.1 - Title` (hyphen with spaces, as in Chapter 6 `[823]`). Image paragraph: centered, `spacing line=259 auto`, inline picture, then caption paragraph, then one empty justified paragraph.
- Chapter 7 figures currently have no typed caption. Their numbers are baked into the PNG title ("Fig. 7.1 - ..." in image20, "Fig. 7.2 - ..." in image21). image22 has no number. The new PNGs have their own titles and no matching numbering, so use typed Word captions below every new Chapter 7 figure in the Chapter 6 style, and make sure no PNG carries a conflicting baked "Fig. 7.x" (see 5).
- Inline image `docPr id` must be unique per image (reuse python-docx `add_picture` through a new run and then move the paragraph).

## 3. Outdated content found (all to be replaced)

| Where | Outdated text |
|---|---|
| Table 7.2 row 1 `[973]` | "101 unaugmented test samples across 20 identities" |
| Table 7.2 row 2 | "107 test samples and 20 gallery classes" |
| 7.5.1 para `[979]` | "Split B classifier evaluation uses 20 student identity classes ... 14,070 augmented training samples, 101 ... validation, 101 ... test" |
| Table 7.3 `[982]` | 20 classes, 14,070, 101, 101, epochs 8, best val 93.07%, train 96.50%, test 90.10%, macro F1 0.8846 |
| `[984]` | "91 correctly classified samples out of 101 ... One class has no correctly classified test samples ..." |
| `[985]` | per-student reliability sentence (keep idea, rewrite) |
| Table 7.4 `[990]` | all 5 rows (107-sample counts, "Identification Accuracy" column) |
| `[992]` | "Each row contains 107 evaluated samples." |
| `[993]` | "highest F1 value, 0.9246, at a threshold of 0.30 ... precision is 91.30% ... F1 value is 0.8796" |
| image20.png `[996]` | old chart (107 samples, 20 gallery classes, 85.98% / 78.50% / 18.69%) |
| 7.5.3 `[999]`, `[1000]`, `[1001]` | old counting rules (false acceptance rate over all samples; recall excluding wrong matches); "counts in Table 7.4" stays valid as a reference |
| `[1035]` | "The earlier advertised F1 value of 0.957 ..." (forbidden, delete) |
| 7.10 `[1091]`, `[1093]` | generic; extend (see 4.9) |
| 7.11 `[1103]` | "90.10% accuracy across 101 test samples and 20 identities" |
| Ch 8.2 `[1132]` | "ResNet classifier achieved 90.10% test accuracy on a limited dataset containing 20 identities" |

Checked and still correct (leave): Table 7.5 (50.00%, 36.50%, 0.3286, 0.3183), Table 7.6 class-wise (recomputed from the matrix: matches), Table 7.7 matrix `[[0,3,9],[1,29,51],[0,36,71]]`, `[1016]` 107 of 200 / 53.50%, `[1028]`, image21 counts (but see 5), 6.5.4 / 4.x text about 112 x 112 and threshold 0.60, 6.5.3 gallery threshold default 0.55.
Ch. 8 `[1116]`, `[1133]` (risk conclusion) already correct.

## 4. Edits in order

### 4.1 Table 7.2 (Evaluation Scope)
- Row "Face classifier evaluation": col2 -> `95 clean test photographs (Split A, 80:10:10) and 138 clean test photographs (Split B, 70:15:15), across 29 identities`; col3 unchanged ("Evaluate ResNet-50 identity classification").
- Row "Gallery threshold sweep": col2 -> `138 Split B test photographs against a 29-identity gallery built from 654 training photographs`; col3 unchanged.
- Other rows unchanged. Intro `[970]` "The recorded experiments use different datasets..." unchanged.

### 4.2 7.5.1 intro `[979]` -> replace with two paragraphs (generic, no names/IDs)
P1: "The classifier was trained and evaluated on face crops from 29 identity classes. A total of 947 photographs were audited, 17 were excluded because the face was wrong or could not be detected, and 930 were used. Each photograph contributes one clean face crop and 30 augmented variants, giving 28,830 samples. Between 25 and 41 photographs were used per identity (median 32)."
P2: "Samples were split by source photograph, so no photograph contributes to more than one of the training, validation and test sets. Validation and test sets contain only clean (unaugmented) crops. Two splits were evaluated: Split A (80:10:10) with 740, 95 and 95 photographs (22,940 training samples), and Split B (70:15:15) with 654, 138 and 138 photographs (20,274 training samples). The model is an ImageNet-pretrained ResNet-50 with a new 29-way output layer, 112 x 112 input, Adam (learning rate 1e-4), label smoothing 0.1, class-weighted cross-entropy, early stopping with patience 7, a maximum of 30 epochs and seed 42. The checkpoint was chosen on validation accuracy only, and the test set was not used for tuning. The Split B checkpoint is the one used by the application, with its acceptance threshold of 0.60."
(Drop "Split B ... recorded" wording. "Split A/B" terms are defined here.)

### 4.3 Table 7.3 -> three columns, caption unchanged text "Table 7.3 ResNet-50 Classifier Results"
Header: `Metric | Split A (80:10:10) | Split B (70:15:15)`. Add a third cell by deep-copying column 2 cells.

| Metric | Split A | Split B |
|---|---|---|
| Number of identity classes | 29 | 29 |
| Training samples | 22,940 | 20,274 |
| Validation photographs | 95 | 138 |
| Test photographs | 95 | 138 |
| Input image size | 112 × 112 pixels | 112 × 112 pixels |
| Epochs completed | 8 | 10 |
| Selected epoch | 1 | 3 |
| Best validation accuracy | 100.00% | 99.28% |
| Final training accuracy | 99.94% | 100.00% |
| Test accuracy | 97.89% (93/95) | 99.28% (137/138) |
| Test accuracy 95% Wilson interval | 92.65% to 99.42% | 96.01% to 99.87% |
| Test macro precision | 0.9845 | 0.9943 |
| Test macro recall | 0.9770 | 0.9914 |
| Test macro F1-score | 0.9774 | 0.9919 |

(Existing rows "Training samples"/"Validation samples"/"Test samples" labels: change "samples" to "photographs" for validation/test to keep consistent; "Training samples" stays samples since it counts augmented crops.)

### 4.4 Text after Table 7.3 (`[984]`, `[985]`) -> replace by
- "Split A classified 93 of 95 test photographs correctly (97.89%) and Split B classified 137 of 138 (99.28%). In Split A the validation accuracy was 100.00% at every epoch, so validation gave no basis for choosing between epochs and the first epoch was kept. The test sets are small. Each student has only 3 to 4 (Split A) or 4 to 6 (Split B) test photographs, so a single photograph changes one student's accuracy by 17 to 33 percentage points, and the confidence intervals in Table 7.3 are wide."
- "All misclassified photographs (two in Split A, one in Split B) had a confidence below the application threshold of 0.60 (0.27 and 0.12 in Split A, 0.33 in Split B). In the application they would therefore be rejected rather than assigned to another student."
- "The training loss plateaus near 0.66 in Figure 7.1 because label smoothing of 0.1 sets a floor on the loss. It does not indicate underfitting."
- Keep a version of old `[985]`: "These results demonstrate classifier feasibility on the evaluated closed set of enrolled students. They do not establish equal reliability for every student or performance on non-enrolled people, small or occluded faces, or multi-face classroom scenes."

### 4.5 New figures in 7.5.1 (Split B only; Split A described in table/text). Insert after the 4.4 paragraphs, each = picture paragraph + caption + empty para
Source folder `training_results\expanded_v3\graphs_report\`. Sizes: curves cx=6120130 (cy by aspect), confusion cx=6120130, per-student cx=6120130.
- `curves_splitB.png` - caption `Fig. 7.1 - Training and Validation Loss and Accuracy (Split B, 70:15:15)`
- `confusion_splitB.png` - `Fig. 7.2 - Confusion Matrix on the Split B Test Photographs`
- `per_student_accuracy_splitB.png` - `Fig. 7.3 - Per-Student Test Accuracy (Split B)`
Lead-in sentences (one each, before the figure): "Figure 7.1 shows training and validation loss and accuracy for Split B. Loss includes label smoothing of 0.1." / "Figure 7.2 shows the confusion matrix for the 138 Split B test photographs; one photograph is off the diagonal." / "Figure 7.3 shows test accuracy for each of the 29 identities, identified only by anonymous labels S01 to S29, with the overall test accuracy as a dashed line."
No Split A figures (the report has no paired A/B figure layout).

### 4.6 7.5.2 Gallery Threshold Evaluation (`[987]` ... `[997]`)
- `[987]` -> "The gallery matching evaluation compares cosine similarity thresholds from 0.20 to 0.80 on the 29-identity data. The gallery holds one mean ArcFace embedding per identity, computed from the clean crops of the 654 Split B training photographs. The probes are the 138 clean Split B test crops. Each probe is matched to its top-1 gallery identity and accepted only if the cosine similarity is at least the threshold."
- Table 7.4 caption -> `Table 7.4 Selected Gallery Matching Results` (unchanged). Columns -> `Threshold | Correct Matches | Wrong-Identity Matches | Rejected Samples | Precision | Recall | F1-score` (add 2 cells by deep-copy, rename the last column). Rows (all values from `graphs_report\gallery_threshold_splitB.csv`; the executor must read the CSV for the other columns, and for 0.30/0.40/0.70/0.80 compute precision=c/(c+w), recall=c/138, F1 = harmonic mean, 4 decimals):
  - 0.30: 131 / 5 / 2
  - 0.40: 130 / 2 / 6
  - 0.55: 125 / 0 / 13, precision 1.0000, recall 0.9058, F1 0.9506
  - 0.70: 105 / 0 / 33
  - 0.80: 67 / 0 / 71
  Optionally add a row 0.20 (or 0.25): 133 / 5 / 0 with the best F1 0.9638. Keep 5 or 6 rows; the best-F1 row should be included so the text matches the table.
- `[992]` -> "Each row contains 138 evaluated probes. Precision is correct / (correct + wrong-identity), recall is correct / 138, and F1 is their harmonic mean."
- `[993]` -> "The highest F1 value, 0.9638, occurs at thresholds 0.20 and 0.25 (133 correct, 5 wrong-identity, 0 rejected). At the application threshold of 0.55 the precision is 1.0000, the recall is 0.9058 and the F1 value is 0.9506 (125 correct, 0 wrong-identity, 13 rejected). No wrong-identity match is accepted at any threshold from 0.50 upward. Without a threshold, the top-1 match is correct for 133 of the 138 probes."
- `[994]` keep (trade-off sentence is still true).
- Replace image20.png `[996]` with `gallery_threshold_splitB.png`; caption below: `Fig. 7.4 - Effect of Cosine Similarity Threshold on Gallery Matching (Split B)`; add lead-in "Figure 7.4 plots precision, recall and F1 together with the wrong-identity and rejection rates; the dotted line marks the application threshold of 0.55." Remove the old picture part from the package (drop relationship rId28/image20 if no longer referenced).

### 4.7 7.5.3 Interpretation of Recognition Metrics
- `[999]` -> "In the threshold evaluation, precision counts only accepted matches, so wrong-identity matches reduce precision but rejections do not. Recall divides correct matches by all 138 probes, so rejections reduce recall. The wrong-identity rate is wrong-identity matches divided by all probes. This is not equivalent to an impostor false acceptance rate measured with non-enrolled people."
- `[1000]` -> delete (old recall definition) or merge into `[999]`.
- `[1001]` -> "The counts in Table 7.4 give a direct description of the observed outcomes."
- `[1002]` keep. Add one sentence: "All probes are clean single-face crops of enrolled students. Rejection of non-enrolled people has not been tested because no such photographs were available."

### 4.8 7.6 Academic Risk Model Results
- Keep `[1009]`-`[1011]`, `[1013]` Table 7.5 and its numbers, Tables 7.6 and 7.7.
- Add `[1011]` extra sentence: "The split uses random_state 42." (optional; skip if unsure).
- After `[1017]` (ends "...predictive usefulness.") add the new bar chart: lead-in "Figure 7.5 compares the accuracy and macro F1-score of the two models and shows the majority-class baseline of 53.50%." (omit the baseline half if the PNG does not draw it; the executor must check the PNG.) Picture `risk_model_comparison.png`, caption `Fig. 7.5 - Accuracy and Macro F1-score of the Academic Risk Models`. Do not use any percentage other than 50.00 / 36.50 / 0.3286 / 0.3183 / 53.50.
- Confusion-matrix figure `[1030]` (image21.png): counts already match 0/3/9, 1/29/51, 0/36/71, so **keep the image**, but it has the baked title "Fig. 7.2 - Confusion Matrix for XGBoost ..." which conflicts with the new numbering. Plan: re-render it from the same counts (read from `evaluation\results\risk_model_evaluation.json`) with the title "Confusion Matrix for XGBoost Academic Risk Classification" and no "Fig." prefix, save as `graphs_report\risk_confusion_matrix_report.png` (300 dpi, white), then use it with the caption `Fig. 7.6 - Confusion Matrix for XGBoost Academic Risk Classification`. Fallback if re-render is not allowed: renumber the other figures so that the risk confusion matrix stays "Fig. 7.2"; this is worse because the classifier figures come first. The picture paragraph currently sits after the Table 7.7 text; keep its position, add caption below, keep width 3,279,026 x 2,914,650 EMU (or scale to ~4.5 inch).
- `[1035]` (0.957 sentence): delete the paragraph.
- `[1016]`/`[1017]` unchanged (still true).
- `[1022]` keep.

### 4.9 Limitations 7.10
- `[1091]` -> "Recognition test sets are small: each identity has only a few test photographs, and the confidence intervals are wide."
- `[1093]` -> "Test crops are clean single-face crops of enrolled students (closed set). Non-enrolled faces, small back-row faces, occlusion and multi-face classroom scenes were not evaluated, and rejection of non-enrolled people has not been tested. Dedicated impostor and presentation-attack testing is insufficient to establish biometric security."
- `[1094]`/`[1095]`: `[1094]` append "The risk model is trained and tested on synthetic data and does not exceed the majority-class baseline." `[1095]` keep.

### 4.10 Summary 7.11 `[1103]` and Chapter 8.2 `[1132]`
- `[1103]` -> "The face-classifier evaluation covers 29 identities. Split A reached 97.89% test accuracy on 95 photographs and Split B reached 99.28% on 138 photographs, with small test sets and wide confidence intervals. In the gallery threshold experiment, no wrong-identity match is accepted from a threshold of 0.50 upward, at the cost of rejecting more enrolled students as the threshold rises." (2nd sentence of the old `[1103]` re: trade-off folded in.)
- `[1132]` first two sentences -> "The recorded evaluation demonstrates useful capabilities while identifying important limitations. The ResNet-50 classifier reached 99.28% test accuracy (137 of 138 photographs) on 29 identities in the configuration used by the application, evaluated on a small closed set of clean face crops. The gallery-matching experiment showed that increasing the cosine similarity threshold removed wrong-identity matches while increasing rejection of enrolled students." Keep the last sentence ("These findings highlight the need ...").

## 5. Figure and table numbering after the edit

| New | Content | Source |
|---|---|---|
| Fig. 7.1 | Training and validation loss/accuracy, Split B | curves_splitB.png |
| Fig. 7.2 | Confusion matrix, Split B | confusion_splitB.png |
| Fig. 7.3 | Per-student test accuracy, Split B | per_student_accuracy_splitB.png |
| Fig. 7.4 | Gallery threshold sweep, Split B | gallery_threshold_splitB.png (replaces image20) |
| Fig. 7.5 | Risk model accuracy and macro F1 bar chart (new) | risk_model_comparison.png |
| Fig. 7.6 | XGBoost risk confusion matrix | re-rendered image21 (title without baked number) |

- Table numbers 7.1 to 7.12 are unchanged (no table added or removed). Table 7.3 and 7.4 get more columns/rows only.
- Chapter 6 figures (6.1 to 6.9) are unaffected. image22 (processing-time chart) stays unnumbered.
- In-text references: Chapter 7 currently has no "Figure x" references and no references to Table 7.3 or 7.5; only `[1001]` ("Table 7.4") and `[1077]` ("Table 7.12") exist, both stay correct. New "Figure 7.x" references are added in the lead-ins above.
- List of Figures / List of Tables / TOC: none exist in this docx. Nothing to update.
- Removed figures: image20.png (gallery chart with 107 samples / 20 classes / 85.98% / 78.50% / 18.69%). image21.png is replaced by its re-rendered version because of its baked "Fig. 7.2" label only (its counts are correct). The package will keep image22 and all Chapter 1-6 images.

## 6. Checks for the executor (step 2)
- Before inserting each PNG, open it and confirm: white background, no baked "Fig. 7.x" prefix that disagrees with the table above, no student names/USNs (anonymous S01 to S29 only), no "v3", no 98.6% / 93.1%, no 107 / 20 classes. If a PNG carries a baked figure number, either regenerate it without one or match the typed caption to it.
- After editing, dump the docx again and grep for: `90.10`, `0.957`, `98.6`, `93.1`, `107 `, `20 identit`, `20 student`, `20 gallery`, `14,070`, `101 `, `0.8846`, `0.9246`, `v3`, `USN`. Only "107 of the 200 records" (risk majority class) and "107" in Table 7.6 (High test samples) may remain.
- Confirm element order: caption above for tables, below for figures; the risk Table 7.7 text `[1028]` still precedes its figure.
- Do not touch Chapter 1-6 text, references, header/footer, or the front matter (none present).
- Save only to `3Report (1)_updated.docx`; do not commit.

## 7. Open points to flag to the user
- This docx has no title page, certificate, acknowledgements, TOC, List of Figures or List of Tables, so none were edited.
- 7.5.4 "Pilot Evidence" (14 images of two students; seven recognized students) is outside the scope; it is left unchanged. It refers to "earlier project documentation", which might be considered an earlier-experiment reference.
- Table 7.2 and `[939]` ("previously recorded experiments") stay as they are.
