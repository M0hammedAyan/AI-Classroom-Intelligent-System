# Gallery-threshold chart and risk-model chart: results and provenance

## Task 1. 29-student gallery-threshold chart

Files: `graphs_report/gallery_threshold_splitB.png` (1890x1170, 300 dpi, white), `graphs_report/gallery_threshold_splitB.csv`, script `make_gallery_chart.py`.
The file name uses `splitB` with no space (the request wrote `split B`).

The existing JSON `evaluation/results/gallery_threshold_29class_splitB.json` had 12 of the 13 thresholds. It lacked 0.75, so `make_gallery_chart.py` recomputes the full sweep 0.20 to 0.80 with the same gallery and probe definition as `evaluate_gallery_29class.py` (29 students, 654 gallery photos, 138 probes). It asserts the counts equal the JSON for the 12 overlapping thresholds. All 12 matched. The existing JSON was not modified.

Plotted values (precision = correct/(correct+wrong), recall = correct/138, F1 = harmonic mean of those two):

| Threshold | Correct | Wrong | Rejected | Precision | Recall | F1 | Wrong rate | Reject rate |
|---|---|---|---|---|---|---|---|---|
| 0.20 | 133 | 5 | 0 | 0.9638 | 0.9638 | 0.9638 | 0.0362 | 0.0000 |
| 0.25 | 133 | 5 | 0 | 0.9638 | 0.9638 | 0.9638 | 0.0362 | 0.0000 |
| 0.30 | 131 | 5 | 2 | 0.9632 | 0.9493 | 0.9562 | 0.0362 | 0.0145 |
| 0.35 | 131 | 3 | 4 | 0.9776 | 0.9493 | 0.9632 | 0.0217 | 0.0290 |
| 0.40 | 130 | 2 | 6 | 0.9848 | 0.9420 | 0.9630 | 0.0145 | 0.0435 |
| 0.45 | 129 | 1 | 8 | 0.9923 | 0.9348 | 0.9627 | 0.0072 | 0.0580 |
| 0.50 | 128 | 0 | 10 | 1.0000 | 0.9275 | 0.9624 | 0.0000 | 0.0725 |
| 0.55 | 125 | 0 | 13 | 1.0000 | 0.9058 | 0.9506 | 0.0000 | 0.0942 |
| 0.60 | 123 | 0 | 15 | 1.0000 | 0.8913 | 0.9425 | 0.0000 | 0.1087 |
| 0.65 | 118 | 0 | 20 | 1.0000 | 0.8551 | 0.9219 | 0.0000 | 0.1449 |
| 0.70 | 105 | 0 | 33 | 1.0000 | 0.7609 | 0.8642 | 0.0000 | 0.2391 |
| 0.75 | 91 | 0 | 47 | 1.0000 | 0.6594 | 0.7948 | 0.0000 | 0.3406 |
| 0.80 | 67 | 0 | 71 | 1.0000 | 0.4855 | 0.6537 | 0.0000 | 0.5145 |

The chart has precision, recall and F1 on the left axis (Score, 0 to 1.05) and wrong-identity rate and rejection rate on the right axis (Rate, fraction of 138 probes). Each series has its own line style and marker. There is one combined legend and a dotted vertical line labelled "Application threshold (0.55)". It has no "Optimal" annotation and no old-dataset text. I viewed the PNG and it is legible.

Issues:
- Table 7.4 in the docx lists counts that sum to 138 per row (for example 131+5+2). The text under it still says "Each row contains 107 evaluated samples", and the paragraph giving "highest F1 0.9246 at 0.30" and "precision 91.30%, F1 0.8796" at 0.55 is the old 107-sample result. Table 7.4's percentages (94.93%, 94.20%, 90.58%, 76.09%, 48.55%) match the 138-probe sweep above.
- The docx Fig 7.1 (`word/media/image20.png`) is the old chart. Its subtitle says "107 test samples across 20 gallery classes", and its values (85.98%, 78.50%, 14.02%) are not the 29-student results.

## Task 2. Risk-model chart

Files: `graphs_report/risk_model_comparison.png` (1890x1080, 300 dpi), `graphs_report/risk_model_comparison.csv`, script `make_risk_chart.py`.
The chart is a grouped bar chart of Accuracy and Macro F1 for XGBoost and Logistic Regression: 0.5000 / 0.3286 and 0.3650 / 0.3183, as in Table 7.5. Every bar is filled and carries a value label. A dashed line marks the majority-class accuracy baseline at 0.535. That baseline comes from the docx text in 7.6.2 (107 of 200) and from the JSON class supports, so it is not invented. The title is "Academic Risk Model Comparison on the Held-Out Test Set (n = 200)". I viewed the PNG and it is legible.

### Verbatim docx tables (read-only via python-docx)

**Table 7.5 Academic Risk Model Comparison**

| Metric | XG Boost  | Logistic Regression |
|---|---|---|
| Accuracy | 50.00% | 36.50% |
| Macro F1-score | 0.3286 | 0.3183 |

(The docx writes "XG Boost" with a space.) The docx values equal the values plotted.

**Table 7.6 XG Boost  Class-Wise Results**

| Risk Category | Test Samples | Precision | Recall | F1-score |
|---|---|---|---|---|
| Low | 12 | 0.00% | 0.00% | 0.0000 |
| Medium | 81 | 42.65% | 35.80% | 0.3893 |
| High | 107 | 54.20% | 66.36% | 0.5966 |

**Table 7.7 XG Boost  Confusion Matrix**

| Actual Category | Predicted Low | Predicted Medium | Predicted High |
|---|---|---|---|
| Low | 0 | 3 | 9 |
| Medium | 1 | 29 | 51 |
| High | 0 | 36 | 71 |

Section 7.6 text:
- 7.6.1: "The recorded risk-model evaluation uses 1,000 synthetic student records. A stratified split assigns 800 records to training and 200 records to testing." Features: overall attendance, recent attendance, average score, recent score, failed subjects.
- 7.6.2: The largest test category holds 107 of the 200 records, so predicting it for every record gives 53.50% accuracy. The XGBoost accuracy therefore does not exceed this majority-class baseline.
- 7.6.3: The model finds no low-risk test record correctly.
- 7.6.4: The matrix shows a tendency to assign records to high risk, and 36 actual high-risk records are predicted as medium.
- 7.6.5: "The earlier advertised F1 value of 0.957 should not replace the recorded results presented here without a clearly documented experiment, dataset, and evaluation procedure."

### The "old risk chart"

Section 7.6 contains exactly one image, `word/media/image21.png`, extracted to `graphs_report/_old_risk_chart_extracted.png`. It is **Fig. 7.2, the XGBoost confusion matrix**, not a bar chart. Title: "Fig. 7.2 - Confusion Matrix for XGBoost Academic Risk Classification". Subtitle: "Synthetic dataset, 200 held-out test records, cell values are counts". Cells: 0/3/9, 1/29/51, 0/36/71. Footer: "Correct classifications: 100 / 200 (50.00%)" and "Actual class totals: Low 12 | Medium 81 | High 107". It is consistent with Tables 7.5, 7.6 and 7.7 (diagonal 0+29+71 = 100 = 50.00%; row sums 12/81/107).

**The docx contains no bar chart with 98.6% / 93.1% legend values or blank bars.** The docx text has no "98.6" or "93.1", and its only 0.957 is the warning sentence in 7.6.5. `git grep` for 98.6 and 93.1 in code and docs finds nothing relevant either. The only other chapter 7 images are image20 (gallery Fig 7.1) and image22 (a timing figure). The chart you describe is most likely a different file or draft outside this docx and repo. If you send it, I can identify its source.

### Provenance of each risk number

| Number | Source | Dataset and split | Current recorded result? |
|---|---|---|---|
| 50.00% accuracy (XGBoost) | `evaluation/results/risk_model_evaluation.json` (`xgboost.accuracy` 0.5), written by `evaluation/evaluate_risk_model.py`; AUDIT.md:372; CLAIMS_TABLE.md:27 (C-19); FINAL_REPORT.md:1065 | `vista/ml/data/student_data.csv`, synthetic, 1,000 rows, stratified 80/20, `random_state=42`: 800 train / 200 test | **Yes, true recorded value** |
| 0.3286 macro F1 (XGBoost) | same JSON (`macro_f1`); AUDIT.md:372; CLAIMS_TABLE.md:27 | same | **Yes** |
| 36.50% accuracy (LR) | same JSON (`logistic_regression.accuracy` 0.365); AUDIT.md:373; FINAL_REPORT.md:1065 | same (scaled, `class_weight="balanced"`) | **Yes** |
| 0.3183 macro F1 (LR) | same JSON; AUDIT.md:373 | same | **Yes** |
| 53.5% majority baseline (107/200) | not a stored field. CLAIMS_TABLE.md:28 (C-20) derives it from the JSON supports 12/81/107; docx 7.6.2 | test split of the same CSV; full set HIGH 535, MEDIUM 405, LOW 60 | **Yes** (derived; re-verified in the re-run) |
| 0.957 macro F1 | AUDIT.md:377-378 ("Historical Run on 200 Balanced Synthetic Records": accuracy 95.00%, F1 0.957). It also persists in stale docs: `vista/ml/CLAUDE.md`, `vista/README.md`, `vista/PROJECT_REPORT.md`, `vista/PLANB.md`, NEEDS_YOUR_INPUT.md:48, DOCS_SYNC_REPORT.md:48. `vista/ml/train.py:167` only prints the F1 at train time and stores no metric | An earlier, smaller, balanced synthetic set of about 200 rows, no longer in the repo. AUDIT.md says F1 fell to about 0.329 when the data grew to 1,000 imbalanced rows | **No.** Historical, different experiment |
| 98.6% and 93.1% | **Not found** in the docx, repo text, JSON or `model.pkl` | unknown | **No recorded source. Treat as wrong.** |

`vista/ml/model.pkl` holds the model, `model_name` ("XGBoost"), scaler (None), features and label maps. It stores no metrics. `train.py:158` splits 80/20 stratified with `random_state=42`, the same split the evaluation script uses. I did not retrain it.

Why the numbers contradict: 0.957 comes from an older, balanced 200-row synthetic set. The current 1,000-row CSV is imbalanced (53.5% HIGH, 6% LOW), and XGBoost on it scores 50.00% and 0.3286. Both datasets are synthetic and rule-labelled. The two results describe different experiments, so only the 50.00% / 0.3286 / 36.50% / 0.3183 numbers belong with Table 7.5. The 98.6% / 93.1% values have no traceable source.

### Re-run

I re-ran the evaluation logic in a temporary script, since deleted (the original script writes a fixed output path, so I did not run it directly). It uses the same split, models and hyperparameters, and writes `evaluation/results/risk_model_evaluation_rerun.json`. **It reproduced exactly**:
- XGBoost: accuracy 0.5, macro F1 0.3286, confusion matrix [[0,3,9],[1,29,51],[0,36,71]].
- Logistic Regression: accuracy 0.365, macro F1 0.3183, confusion matrix [[6,0,6],[37,19,25],[34,25,48]].
- 1,000 rows, 200 test, majority class 107 of 200.

The `matches_existing` flags in the rerun JSON are true for both models. The original JSON was not overwritten and `model.pkl` was not touched.

## Created files
- `training_results/expanded_v3/make_gallery_chart.py`
- `training_results/expanded_v3/make_risk_chart.py`
- `training_results/expanded_v3/REPORT_CHARTS_RISK_GALLERY.md`
- `training_results/expanded_v3/graphs_report/gallery_threshold_splitB.png` and `.csv`
- `training_results/expanded_v3/graphs_report/risk_model_comparison.png` and `.csv`
- `training_results/expanded_v3/graphs_report/_old_risk_chart_extracted.png` (docx image21, Fig 7.2 confusion matrix)
- `training_results/expanded_v3/graphs_report/_old_gallery_chart_extracted.png` (docx image20, old Fig 7.1)
- `evaluation/results/risk_model_evaluation_rerun.json`

Nothing was committed or pushed. `Final report.docx` and all existing results, models and app code are unchanged.

## Issues to resolve in the report
1. The 98.6% / 93.1% blank-bar chart is not in this docx. Section 7.6 has only the Fig 7.2 confusion matrix, which is consistent with Tables 7.5 to 7.7. Replace or add the new `risk_model_comparison.png` if you want a bar chart.
2. Gallery text is mixed. Table 7.4 uses 138-probe counts, but the sentence "Each row contains 107 evaluated samples", the F1 0.9246 / precision 91.30% / F1 0.8796 paragraph, Table 7.2 row 2 and old Fig 7.1 still describe the old 107-sample, 20-class run.
3. Stale 0.957 claims remain in `vista/ml/CLAUDE.md`, `vista/README.md`, `vista/PROJECT_REPORT.md`, `vista/PLANB.md` and NEEDS_YOUR_INPUT.md. I did not edit them.
