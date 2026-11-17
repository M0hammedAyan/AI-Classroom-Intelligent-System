# Report Update Changelog

Input: `3Report (1).docx` (unchanged). Output: `3Report (1)_updated.docx` (PDF: `3Report (1)_updated.pdf`).

## Figures

| Figure | Caption | Status |
|---|---|---|
| Fig. 7.1 | Training and Validation Loss and Accuracy (Split B, 70:15:15) | added |
| Fig. 7.2 | Confusion Matrix on the Split B Test Photographs | added |
| Fig. 7.3 | Per-Student Test Accuracy (Split B) | added |
| Fig. 7.4 | Effect of Cosine Similarity Threshold on Gallery Matching (Split B) | replaces old gallery threshold chart (old chart removed) |
| Fig. 7.5 | Accuracy and Macro F1-score of the Academic Risk Models | added |
| Fig. 7.6 | Confusion Matrix for XGBoost Academic Risk Classification | re-rendered from the same counts, old number baked into image title removed |

Counts: inline images 20 before, 24 after. Figure captions (Fig. x.y) 9 before, 15 after. Tables 27 before and after; table captions 24 before and after (Table numbers 7.1 to 7.12 unchanged).

## Tables changed

- Table 7.2 (Evaluation Scope): classifier and gallery rows.
- Table 7.3: rewritten as Split A vs Split B (15 rows x 3 columns).
- Table 7.4: rewritten, 7 columns, thresholds 0.20, 0.30, 0.40, 0.55, 0.70, 0.80.
- Tables 7.5 to 7.7: already matched current results, unchanged.

## Paragraph changes (old text -> new text)

### replace (old paragraphs 826-827, new 826-828)
Section: 7.5.1 ResNet-50 Classifier Results

- OLD: The recorded Split B classifier evaluation uses 20 student identity classes. The training record reports 14,070 augmented training samples, 101 unaugmented validation samples, and 101 unaugmented test samples.
- NEW: The classifier was trained and evaluated on face crops from 29 identity classes. A total of 947 photographs were audited, 17 were excluded because the face was wrong or could not be detected, and 930 were used. Each photograph contributes one clean face crop and 30 augmented variants, giving 28,830 samples. Between 25 and 41 photographs were used per identity (median 32).
- NEW: Samples were split by source photograph, so no photograph contributes to more than one of the training, validation and test sets. Validation and test sets contain only clean (unaugmented) crops. Two splits were evaluated: Split A (80:10:10) with 740, 95 and 95 photographs (22,940 training samples), and Split B (70:15:15) with 654, 138 and 138 photographs (20,274 training samples). The model is an ImageNet-pretrained ResNet-50 with a new 29-way output layer, 112 × 112 input, Adam (learning rate 1e-4), label smoothing 0.1, class-weighted cross-entropy, early stopping with patience 7, a maximum of 30 epochs and seed 42. The checkpoint was chosen on validation accuracy only, and the test set was not used for tuning. The Split B checkpoint is the one used by the application, with an acceptance threshold of 0.60.

### replace (old paragraphs 828-830, new 829-839)
Section: 7.5.1 ResNet-50 Classifier Results

- OLD: The test accuracy corresponds to 91 correctly classified samples out of 101. However, performance differs across identities. One class has no correctly classified test samples, while other classes achieve complete recognition within their small test subsets.
- OLD: The overall result therefore demonstrates classifier feasibility on the evaluated data but does not establish equal reliability for every student.
- NEW: Split A classified 93 of 95 test photographs correctly (97.89%) and Split B classified 137 of 138 (99.28%). In Split A the validation accuracy was 100.00% at every epoch, so validation gave no basis for choosing between epochs and the first epoch was kept. The test sets are small. Each student has only 3 to 4 (Split A) or 4 to 6 (Split B) test photographs, so a single photograph changes one student's accuracy by 17 to 33 percentage points, and the confidence intervals in Table 7.3 are wide.
- NEW: All misclassified photographs (two in Split A, one in Split B) had a confidence below the application threshold of 0.60 (0.27 and 0.12 in Split A, 0.33 in Split B). In the application they would therefore be rejected rather than assigned to another student.
- NEW: The training loss plateaus near 0.66 in Figure 7.1 because label smoothing of 0.1 sets a floor on the loss. It does not indicate underfitting.
- NEW: These results demonstrate classifier feasibility on the evaluated closed set of enrolled students. They do not establish equal reliability for every student or performance on non-enrolled people, small or occluded faces, or multi-face classroom scenes.
- NEW: Figure 7.1 shows training and validation loss and accuracy for Split B. Loss includes label smoothing of 0.1.
- NEW: Fig. 7.1 - Training and Validation Loss and Accuracy (Split B, 70:15:15)
- NEW: Figure 7.2 shows the confusion matrix for the 138 Split B test photographs. One photograph is off the diagonal.
- NEW: Fig. 7.2 - Confusion Matrix on the Split B Test Photographs
- NEW: Figure 7.3 shows test accuracy for each of the 29 identities, identified only by anonymous labels S01 to S29, with the overall test accuracy as a dashed line.
- NEW: Fig. 7.3 - Per-Student Test Accuracy (Split B)

### replace (old paragraphs 831-832, new 840-841)
Section: 7.5.2 Gallery Threshold Evaluation

- OLD: The gallery matching evaluation compares several cosine similarity thresholds.
- NEW: The gallery matching evaluation compares cosine similarity thresholds from 0.20 to 0.80 on the 29-identity data. The gallery holds one mean ArcFace embedding per identity, computed from the clean crops of the 654 Split B training photographs. The probes are the 138 clean Split B test crops. Each probe is matched to its top-1 gallery identity and accepted only if the cosine similarity is at least the threshold.

### replace (old paragraphs 833-835, new 842-844)
Section: 7.5.2 Gallery Threshold Evaluation

- OLD: Each row contains 107 evaluated samples.
- OLD: The recorded sweep reports its highest F1 value, 0.9246, at a threshold of 0.30. The application’s default threshold is 0.55, where the recorded precision is 91.30% and the reported F1 value is 0.8796.
- NEW: Each row contains 138 evaluated probes. Precision is correct / (correct + wrong-identity), recall is correct / 138, and F1 is their harmonic mean.
- NEW: The highest F1 value, 0.9638, occurs at thresholds 0.20 and 0.25 (133 correct, 5 wrong-identity, 0 rejected). At the application threshold of 0.55 the precision is 1.0000, the recall is 0.9058 and the F1 value is 0.9506 (125 correct, 0 wrong-identity, 13 rejected). No wrong-identity match is accepted at any threshold from 0.50 upward. Without a threshold, the top-1 match is correct for 133 of the 138 probes.

### insert (old paragraphs 836-836, new 845-847)
Section: 7.5.2 Gallery Threshold Evaluation

- NEW: Figure 7.4 plots precision, recall and F1 together with the wrong-identity and rejection rates. The dotted line marks the application threshold of 0.55.
- NEW: Fig. 7.4 - Effect of Cosine Similarity Threshold on Gallery Matching (Split B)

### replace (old paragraphs 837-841, new 848-851)
Section: 7.5.3 Interpretation of Recognition Metrics

- OLD: The threshold evaluation labels wrong-identity matches divided by all test samples as its false acceptance rate. This is not equivalent to a conventional impostor false acceptance rate measured using a dedicated set of non-enrolled individuals.
- OLD: Its reported recall also uses correct matches divided by correct matches plus rejected samples, excluding wrong-identity matches from that denominator.
- OLD: Accordingly, these values should be interpreted using the evaluation’s stated counting rules. The counts in Table 7.4 provide a direct description of the observed outcomes.
- OLD: The threshold sweep evaluates gallery matching. It does not measure the complete deployed combination of gallery matching, classifier fallback, and liveness screening.
- NEW: In the threshold evaluation, precision counts only accepted matches, so wrong-identity matches reduce precision but rejections do not. Recall divides correct matches by all 138 probes, so rejections reduce recall. The wrong-identity rate is wrong-identity matches divided by all probes. This is not equivalent to an impostor false acceptance rate measured with non-enrolled people.
- NEW: The counts in Table 7.4 give a direct description of the observed outcomes.
- NEW: The threshold sweep evaluates gallery matching. It does not measure the complete deployed combination of gallery matching, classifier fallback, and liveness screening. All probes are clean single-face crops of enrolled students. Rejection of non-enrolled people has not been tested because no such photographs were available.

### insert (old paragraphs 853-853, new 863-865)
Section: 7.6.2 Overall Results

- NEW: Figure 7.5 compares the accuracy and macro F1-score of the two models and shows the majority-class accuracy baseline of 0.535.
- NEW: Fig. 7.5 - Accuracy and Macro F1-score of the Academic Risk Models

### insert (old paragraphs 860-860, new 872-873)
Section: 7.6.4 Confusion Matrix

- NEW: Fig. 7.6 - Confusion Matrix for XGBoost Academic Risk Classification

### delete (old paragraphs 863-864, new 876-876)
Section: 7.6.5 Relationship to Rule-Based Assessment

- OLD: The earlier advertised F1 value of 0.957 should not replace the recorded results presented here without a clearly documented experiment, dataset, and evaluation procedure.

### replace (old paragraphs 897-898, new 909-910)
Section: 7.10 Limitations of Evaluation

- OLD: Recognition datasets contain relatively few original test samples per identity.
- NEW: Recognition test sets are small: each identity has only a few test photographs, and the confidence intervals are wide.

### replace (old paragraphs 899-901, new 911-913)
Section: 7.10 Limitations of Evaluation

- OLD: Dedicated impostor and presentation-attack testing is insufficient to establish biometric security.
- OLD: Academic prediction uses synthetic data rather than verified institutional outcomes.
- NEW: Test crops are clean single-face crops of enrolled students (closed set). Non-enrolled faces, small back-row faces, occlusion and multi-face classroom scenes were not evaluated, and rejection of non-enrolled people has not been tested. Dedicated impostor and presentation-attack testing is insufficient to establish biometric security.
- NEW: Academic prediction uses synthetic data rather than verified institutional outcomes. The risk model is trained and tested on synthetic data and does not exceed the majority-class baseline.

### replace (old paragraphs 908-909, new 920-921)
Section: 7.11 Summary

- OLD: The recorded face-classifier evaluation reports 90.10% accuracy across 101 test samples and 20 identities. Gallery threshold results demonstrate a trade-off between accepted matches, wrong identities, and rejections.
- NEW: The face-classifier evaluation covers 29 identities. Split A reached 97.89% test accuracy on 95 photographs and Split B reached 99.28% on 138 photographs, with small test sets and wide confidence intervals. In the gallery threshold experiment, no wrong-identity match is accepted from a threshold of 0.50 upward, at the cost of rejecting more enrolled students as the threshold rises.

### replace (old paragraphs 934-935, new 946-947)
Section: 8.2 Conclusion

- OLD: The recorded evaluation demonstrates useful capabilities while identifying important limitations. The ResNet classifier achieved 90.10% test accuracy on a limited dataset containing 20 identities. The gallery-matching experiment showed that increasing the cosine similarity threshold reduced incorrect acceptance while increasing rejection of valid candidates. These findings highlight the need to calibrate recognition thresholds using representative classroom data.
- NEW: The recorded evaluation demonstrates useful capabilities while identifying important limitations. The ResNet-50 classifier reached 99.28% test accuracy (137 of 138 photographs) on 29 identities in the configuration used by the application, evaluated on a small closed set of clean face crops. The gallery-matching experiment showed that increasing the cosine similarity threshold removed wrong-identity matches while increasing rejection of enrolled students. These findings highlight the need to calibrate recognition thresholds using representative classroom data.

## Table content (new)

### Table index 15 changed
OLD:
    Evaluation | Data or Workload | Purpose
    Face classifier evaluation | 101 unaugmented test samples across 20 identities | Evaluate ResNet-50 identity classification
    Gallery threshold sweep | 107 test samples and 20 gallery classes | Examine cosine-threshold behavior
    Academic risk evaluation | 1,000 synthetic records, divided into 800 training and 200 test records | Compare XG Boost  and logistic regression
    Gallery matching benchmark | Random 512-dimensional vectors with gallery sizes of 30, 100, and 500 | Measure matching execution time
    Classifier timing | Repeated inference using a generated face-sized input | Measure isolated classifier processing time
    Detection timing | Repeated processing of a generated 640 × 480 image | Measure the configured detection call
    Group scaling calculation | Estimated workloads containing 1 to 60 faces | Explore projected processing requirements
NEW:
    Evaluation | Data or Workload | Purpose
    Face classifier evaluation | 95 clean test photographs (Split A, 80:10:10) and 138 clean test photographs (Split B, 70:15:15), across 29 identities | Evaluate ResNet-50 identity classification
    Gallery threshold sweep | 138 Split B test photographs against a 29-identity gallery built from 654 training photographs | Examine cosine-threshold behavior
    Academic risk evaluation | 1,000 synthetic records, divided into 800 training and 200 test records | Compare XG Boost  and logistic regression
    Gallery matching benchmark | Random 512-dimensional vectors with gallery sizes of 30, 100, and 500 | Measure matching execution time
    Classifier timing | Repeated inference using a generated face-sized input | Measure isolated classifier processing time
    Detection timing | Repeated processing of a generated 640 × 480 image | Measure the configured detection call
    Group scaling calculation | Estimated workloads containing 1 to 60 faces | Explore projected processing requirements

### Table index 16 changed
OLD:
    Metric | Recorded Value
    Number of identity classes | 20
    Training samples | 14,070
    Validation samples | 101
    Test samples | 101
    Input image size | 112 × 112 pixels
    Epochs completed | 8
    Best validation accuracy | 93.07%
    Final training accuracy | 96.50%
    Test accuracy | 90.10%
    Test macro F1-score | 0.8846
NEW:
    Metric | Split A (80:10:10) | Split B (70:15:15)
    Number of identity classes | 29 | 29
    Training samples | 22,940 | 20,274
    Validation photographs | 95 | 138
    Test photographs | 95 | 138
    Input image size | 112 × 112 pixels | 112 × 112 pixels
    Epochs completed | 8 | 10
    Selected epoch | 1 | 3
    Best validation accuracy | 100.00% | 99.28%
    Final training accuracy | 99.94% | 100.00%
    Test accuracy | 97.89% (93/95) | 99.28% (137/138)
    Test accuracy 95% Wilson interval | 92.65% to 99.42% | 96.01% to 99.87%
    Test macro precision | 0.9845 | 0.9943
    Test macro recall | 0.9770 | 0.9914
    Test macro F1-score | 0.9774 | 0.9919

### Table index 17 changed
OLD:
    Threshold | Correct Matches | Wrong-Identity Matches | Rejected Samples | Identification Accuracy
    0.30 | 92 | 12 | 3 | 85.98%
    0.40 | 89 | 9 | 9 | 83.18%
    0.55 | 84 | 8 | 15 | 78.50%
    0.70 | 57 | 5 | 45 | 53.27%
    0.80 | 20 | 0 | 87 | 18.69%
NEW:
    Threshold | Correct Matches | Wrong-Identity Matches | Rejected Samples | Precision | Recall | F1-score
    0.20 | 133 | 5 | 0 | 0.9638 | 0.9638 | 0.9638
    0.30 | 131 | 5 | 2 | 0.9632 | 0.9493 | 0.9562
    0.40 | 130 | 2 | 6 | 0.9848 | 0.9420 | 0.9630
    0.55 | 125 | 0 | 13 | 1.0000 | 0.9058 | 0.9506
    0.70 | 105 | 0 | 33 | 1.0000 | 0.7609 | 0.8642
    0.80 | 67 | 0 | 71 | 1.0000 | 0.4855 | 0.6537

## Not changed / out of scope

- Section 7.5.4 Pilot Evidence still begins 'Earlier project documentation reports...' (out of scope).
- Team table (names) outside the scope was left as is.
- Remaining '107' occurrences are correct: High-class row in Table 7.6 and 107 of 200 majority class.
- The document has no List of Figures/Tables or TOC fields; captions are plain text.