"""Builds REPORT_INPUTS_FINAL.md (anonymised) from verified files. Run after make_report_graphs.py,
evaluation/evaluate_gallery_29class.py and check_unenrolled_photos.py."""
import csv
import json
import math
import re
import statistics
import sys
from pathlib import Path

import docx
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / "training_results" / "expanded_v3"
G = V3 / "graphs_report"
sys.stdout.reconfigure(encoding="utf-8")

ev = json.loads((V3 / "eval_results.json").read_text(encoding="utf-8"))
an = json.loads((G / "report_results_anonymised.json").read_text(encoding="utf-8"))
gal = json.loads((ROOT / "evaluation/results/gallery_threshold_29class_splitB.json").read_text(encoding="utf-8"))
un = json.loads((G / "unenrolled_check.json").read_text(encoding="utf-8"))
old = json.loads((ROOT / "evaluation/results/recognition_threshold_sweep.json").read_text(encoding="utf-8"))
ID = {r["usn"]: r["id"] for r in csv.DictReader(open(G / "USN_to_ID_PRIVATE.csv", encoding="utf-8"))}
ids = sorted(ID.values())


def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def macro_f1(cm):
    cm = np.array(cm); f = []
    for i in range(len(cm)):
        tp = cm[i, i]; fp = cm[:, i].sum() - tp; fn = cm[i].sum() - tp
        p = tp / (tp + fp) if tp + fp else 0; r = tp / (tp + fn) if tp + fn else 0
        f.append(2 * p * r / (p + r) if p + r else 0)
    return float(np.mean(f))


# ---- photo counts ----
sc = list(csv.DictReader(open(V3 / "split_counts.csv", encoding="utf-8")))
photos = {r["usn"]: int(r["photos_total"]) for r in sc if r["split"] == "A"}
audited = {r["usn"]: int(r["photos"]) for r in csv.DictReader(open(V3 / "diagnosis/students.csv", encoding="utf-8"))
           if r["usn"] in ID}
test_n = {s: {r["usn"]: int(r["test_photos"]) for r in sc if r["split"] == s} for s in "AB"}
splits = {s: json.loads((V3 / f"splits_{s}.json").read_text(encoding="utf-8")) for s in "AB"}
nz = np.load(ROOT / "data/processed/facial_pipeline_results_expanded_v3.npz", allow_pickle=True)
n_samples = len(nz["labels"]); n_cls = len(set(str(x) for x in nz["labels"]))
stat = lambda d: (min(d.values()), max(d.values()), statistics.median(d.values()))

# ---- docx ----
doc = docx.Document(ROOT / "Final report.docx")
tables = {}
prev = ""
from docx.table import Table
from docx.text.paragraph import Paragraph
for el in doc.element.body.iterchildren():
    if el.tag.endswith("}p"):
        t = Paragraph(el, doc).text.strip()
        if t: prev = t
    elif el.tag.endswith("}tbl"):
        tables[prev] = Table(el, doc)
t72 = tables["Table 7.2 Evaluation Scope"]; t73 = tables["Table 7.3 ResNet-50 Classifier Results"]
t74 = tables["Table 7.4 Selected Gallery Matching Results"]

L = []
w = L.append
w("# Final report inputs (29-student classifier): anonymised\n")
w("All numbers below were recomputed from the checkpoints, `eval_results.json`, history files, split files and the npz, "
  "or read from the named file. Student IDs S01 to S29 follow one fixed mapping used by every graph and table (kept privately, not listed here).\n")

w("## 1. Graphs (`training_results/expanded_v3/graphs_report/`)\n")
w("Six PNGs, 300 dpi, opaque white background, no USNs and no internal labels: `curves_splitA.png`, `curves_splitB.png`, "
  "`confusion_splitA.png`, `confusion_splitB.png`, `per_student_accuracy_splitA.png`, `per_student_accuracy_splitB.png`. "
  "Script: `training_results/expanded_v3/make_report_graphs.py`. The script re-ran both checkpoints on the test clean crops and asserted that "
  "the confusion matrices, per-student correct/total counts and overall accuracy equal `eval_results.json` (all matched: 93/95 and 137/138). "
  "Each PNG was viewed and checked for legibility.\n")
w("| File | Pixels | Title text |\n|---|---|---|")
from PIL import Image
titles = {"curves_splitA": "Training and Validation Loss and Accuracy (Split A, 80:10:10)",
          "curves_splitB": "Training and Validation Loss and Accuracy (Split B, 70:15:15)",
          "confusion_splitA": "Test Confusion Matrix (Split A, 95 test photographs)",
          "confusion_splitB": "Test Confusion Matrix (Split B, 138 test photographs)",
          "per_student_accuracy_splitA": "Per-Student Test Accuracy (Split A, 80:10:10)",
          "per_student_accuracy_splitB": "Per-Student Test Accuracy (Split B, 70:15:15)"}
for k, t in titles.items():
    im = Image.open(G / f"{k}.png")
    w(f"| {k}.png | {im.size[0]} x {im.size[1]} | {t} |")
w("\nCurves: loss axis is labelled \"Loss (with label smoothing 0.1)\"; the kept checkpoint is a dashed vertical line "
  "(\"Selected checkpoint (epoch 1)\" for A, \"(epoch 3)\" for B). Per-student charts: one bar colour, dashed line at overall test accuracy "
  "(97.89% for A, 99.28% for B). Confusion matrices: all 29 labels on both axes, every non-zero cell annotated.\n")

w("## 2. Gallery threshold experiment (Table 7.4)\n")
w("### 2.1 What the report's Table 7.4 contains\n")
w("Caption: `Table 7.4 Selected Gallery Matching Results`. Paragraph after the table: `Each row contains 107 evaluated samples.` "
  "Section 7.5.2 starts: `The gallery matching evaluation compares several cosine similarity thresholds.` Table 7.2 row 2 reads: "
  f"`{' | '.join(c.text for c in t72.rows[2].cells)}`.\n")
w("| " + " | ".join(c.text for c in t74.rows[0].cells) + " |\n|---|---|---|---|---|")
for r in t74.rows[1:]:
    w("| " + " | ".join(c.text for c in r.cells) + " |")
w("")
w(f"### 2.2 What produced it\n")
w(f"`evaluation/evaluate_recognition.py` wrote `evaluation/results/recognition_threshold_sweep.json`, which records dataset `{old['dataset']}` "
  f"(the earlier npz, not the 29-student file), **{old['total_gallery_classes']} gallery classes and {old['test_sample_count']} test samples**. "
  "So it was NOT run on the 29-student data. Its gallery was the mean of about 70% of the unaugmented crops, chosen by a hash of the source-image name (Python string hashing, which varies between runs) "
  "or, if fewer than 50 test crops resulted, by a seeded random 70/30 split; the split is therefore not reproducible from the script alone. Thresholds were 0.30 to 0.80 in steps of 0.05. "
  "Table 7.4 shows five of them (0.30, 0.40, 0.55, 0.70, 0.80); its \"Identification Accuracy\" column is correct/107.\n")
w("### 2.3 Re-run on the 29-student data (Split B)\n")
w(f"Script: `evaluation/evaluate_gallery_29class.py`. Results: `evaluation/results/gallery_threshold_29class_splitB.json`.\n")
w(f"- Students (gallery classes): **{gal['num_students']}**. Probe samples: **{gal['total_probe_samples']}** (Split B test clean crops, one per test photograph).")
w(f"- Gallery: per-student mean of the L2-normalised ArcFace embeddings of the clean crops of that student's Split B training photos only "
  f"({gal['gallery_photos']} photographs), re-normalised. Database embeddings were not used, so no test photograph is in the gallery.")
w("- Each probe is matched to its top-1 prototype by cosine similarity; it is accepted if that similarity is at or above the threshold.")
w("- Definitions: accepted correct = top-1 is the true student and similarity >= threshold; accepted wrong identity = top-1 is another student and similarity >= threshold; "
  "rejected = top-1 similarity < threshold; precision = correct / (correct + wrong); recall = correct / 138 (all probes, equal to identification accuracy); "
  "F1 = 2PR/(P+R).")
w("- The original script defines recall differently: correct / (correct + rejected), which leaves wrong-identity accepts out of the denominator. "
  "That variant is given in the last two columns so the two definitions can be told apart.\n")
w("| Threshold | Accepted correct | Accepted wrong identity | Rejected | Precision | Recall (correct/138) | F1 | Recall, original definition | F1, original definition |\n|---|---|---|---|---|---|---|---|---|")
for s in gal["threshold_sweep"]:
    w(f"| {s['threshold']:.2f} | {s['accepted_correct']} | {s['accepted_wrong_identity']} | {s['rejected']} | {s['precision']:.4f} | {s['recall']:.4f} | {s['f1']:.4f} | {s['recall_original_definition']:.4f} | {s['f1_original_definition']:.4f} |")
a = gal["at_application_threshold"]
w(f"\n- Best F1 (recall = correct/138): **{gal['best_f1']:.4f}** at thresholds **{', '.join(f'{t:.2f}' for t in gal['best_f1_thresholds'])}** (tie: the two thresholds give identical counts, 133 correct, 5 wrong identity, 0 rejected). "
  f"With the original recall definition the best F1 is {gal['best_f1_original_definition']:.4f} at the same thresholds.")
w(f"- At the application threshold 0.55: {a['accepted_correct']} correct, {a['accepted_wrong_identity']} wrong identity, {a['rejected']} rejected out of {a['total']}; "
  f"precision {a['precision']:.4f}, recall {a['recall']:.4f}, F1 {a['f1']:.4f}.")
w(f"- Without any threshold, top-1 is correct for {gal['top1_correct_without_threshold']} of 138 probes. The 5 wrong top-1 matches have similarities "
  f"{', '.join(f'{x:.3f}' for x in sorted(gal['top1_similarity_wrong']))}; the lowest similarity of a correct match is {gal['top1_similarity_correct_min']:.3f}.")
w("- The threshold trades recall for precision: raising it from 0.20 to 0.50 removes all 5 wrong-identity accepts, and by 0.50 precision is 1.0000 while 10 probes are rejected. "
  "This is a different experiment from Table 7.4 (different gallery source, 29 instead of 20 students, 138 instead of 107 probes), and the numbers are not meant to be merged into that table row by row.\n")

w("## 3. Verbatim report text\n")
w("### 3.1 Table 7.2 (Evaluation Scope), row 1 (first data row, all cells; header row is `Evaluation | Data or Workload | Purpose`)\n")
w("```\n" + "\n".join(repr(c.text) for c in t72.rows[1].cells) + "\n```\n")
w("### 3.2 Full current Table 7.3\n")
w("Caption: `Table 7.3 ResNet-50 Classifier Results`\n")
w("| " + " | ".join(c.text for c in t73.rows[0].cells) + " |\n|---|---|")
for r in t73.rows[1:]:
    w("| " + " | ".join(c.text for c in r.cells) + " |")
w("\n(These are the current 20-class values in the report, pasted verbatim as requested.)\n")

w("## 4. Misclassified test photographs and test counts\n")
for s, lab in (("A", "Split A (95 test photographs)"), ("B", "Split B (138 test photographs)")):
    w(f"### {lab}\n")
    w("Confidence is the softmax probability of the predicted class, from the checkpoint run on the test clean crops (RGB, resize 112 x 112 bilinear, ToTensor, normalise mean 0.5 std 0.5, as in `train_expanded_v3.py`). "
      f"Accuracy reproduced: {an[s]['correct']}/{an[s]['n']}, equal to `eval_results.json`.\n")
    w("| True ID | Predicted ID | Predicted confidence |\n|---|---|---|")
    for m in an[s]["mis"]:
        w(f"| {m['true']} | {m['pred']} | {m['confidence']:.4f} |")
    w("")
w("### Test photographs per student\n")
w("| ID | Split A test | Split B test |\n|---|---|---|")
inv = {v: k for k, v in ID.items()}
for i in ids:
    w(f"| {i} | {test_n['A'][inv[i]]} | {test_n['B'][inv[i]]} |")
w(f"| Total | {sum(test_n['A'].values())} | {sum(test_n['B'].values())} |\n")

w("## 5. Per-epoch training history and source photographs\n")
for s in "AB":
    w(f"### Split {s} (`graphs_report/epochs_split{s}.csv`)\n")
    w("| epoch | train_loss | train_acc | val_loss | val_acc |\n|---|---|---|---|---|")
    for r in csv.DictReader(open(G / f"epochs_split{s}.csv", encoding="utf-8")):
        w(f"| {r['epoch']} | {r['train_loss']} | {r['train_acc']} | {r['val_loss']} | {r['val_acc']} |")
    w("")
log_ok = []
for s in "AB":
    h = json.loads((V3 / f"history_split{s}.json").read_text(encoding="utf-8"))
    txt = (V3 / f"train_split{s}.log").read_text(encoding="utf-8")
    rows_l = re.findall(r"Epoch (\d+)/30 tr_loss=([\d.]+) tr_acc=([\d.]+) vl_loss=([\d.]+) vl_acc=([\d.]+)", txt)
    ok = len(rows_l) == len(h["train_loss"]) and all(
        abs(float(r[1]) - h["train_loss"][k]) < 6e-5 and abs(float(r[2]) - h["train_acc"][k]) < 6e-5 and
        abs(float(r[3]) - h["val_loss"][k]) < 6e-5 and abs(float(r[4]) - h["val_acc"][k]) < 6e-5 for k, r in enumerate(rows_l))
    log_ok.append(f"Split {s}: {len(rows_l)} log epochs, {'all values match history within log rounding (4 dp)' if ok else 'MISMATCH'}")
w("Cross-check against `train_split*.log`: " + "; ".join(log_ok) + ".\n")
mn, mx, md = stat(photos); amn, amx, amd = stat(audited)
w(f"Source photographs per student: used (930) min {mn}, max {mx}, median {md}; audited (947) min {amn}, max {amx}, median {amd}.\n")
w("| ID | Audited photographs | Excluded | Used photographs |\n|---|---|---|---|")
for i in ids:
    u = inv[i]
    w(f"| {i} | {audited[u]} | {audited[u] - photos[u]} | {photos[u]} |")
w(f"| Total | {sum(audited.values())} | {sum(audited.values()) - sum(photos.values())} | {sum(photos.values())} |\n")

w("## 6. Verification of the headline numbers\n")
rows6 = []
rows6.append(("29 classes", n_cls == 29 and len(ID) == 29, f"npz has {n_cls} labels; both checkpoints have 29 classes", "npz labels, splits_*.json"))
rows6.append(("947 photos audited", sum(audited.values()) == 947, f"sum of per-student photo counts = {sum(audited.values())}", "diagnosis/students.csv (AUDIT_V3.md: 947)"))
rows6.append(("17 excluded", sum(audited.values()) - sum(photos.values()) == 17, f"{sum(audited.values())} - {sum(photos.values())} = {sum(audited.values()) - sum(photos.values())}", "students.csv minus split_counts.csv"))
rows6.append(("930 used", sum(photos.values()) == 930, f"sum of photos_total = {sum(photos.values())}", "split_counts.csv"))
rows6.append(("28,830 samples", n_samples == 28830, f"npz has {n_samples} samples (930 x 31)", "npz"))
for s, exp in (("A", (740, 95, 95)), ("B", (654, 138, 138))):
    got = (len(splits[s]["train"]), len(splits[s]["val"]), len(splits[s]["test"]))
    rows6.append((f"Split {s} {exp[0]}/{exp[1]}/{exp[2]} photos", got == exp, f"{got}", f"splits_{s}.json"))
cis = {"A": "92.65-99.42", "B": "96.01-99.87"}
f1s = {"A": 0.9774, "B": 0.9919}
for s, (k, n, pct) in (("A", (93, 95, "97.89")), ("B", (137, 138, "99.28"))):
    e = ev[s]["overall"]; calc = f"{100 * k / n:.2f}"
    rows6.append((f"Test accuracy {s} {pct}% ({k}/{n})", (e["correct"], e["n"]) == (k, n) and calc == pct, f"{e['correct']}/{e['n']} = {calc}%", "eval_results.json; recomputed from checkpoint"))
    lo, hi = wilson(k, n)
    got = f"{100 * lo:.2f}-{100 * hi:.2f}"
    rows6.append((f"Wilson 95% CI {s} {cis[s]}%", got == cis[s], f"recomputed {got}%", "Wilson score formula, z = 1.959964"))
    mf = macro_f1(ev[s]["confusion_matrix"])
    rows6.append((f"Macro F1 {s} {f1s[s]}", f"{mf:.4f}" == f"{f1s[s]:.4f}", f"recomputed {mf:.4f} (eval_results.json: {ev[s]['macro_f1']:.4f})", "from confusion matrix"))
w("| Item | Status | Value found | Source |\n|---|---|---|---|")
for it, ok, val, src in rows6:
    w(f"| {it} | {'CONFIRMED' if ok else 'DIFFERS'} | {val} | {src} |")
w("\nAdditional values used in earlier text: Split A kept checkpoint epoch 1 (validation 100% at every epoch), Split B kept checkpoint epoch 3 (validation 99.28%); "
  "training stopped at epoch 8 (A) and 10 (B).\n")

w("## 7. The five \"non-enrolled person\" photographs\n")
al, sm = un["all_photos_in_folder"], un["the_5_sampled_photos"]
w("Source: the photographs come from the dataset folder of a student who is no longer a class. That folder is deleted from the working tree but is still in git history; "
  "`threshold_check.py` drew a random sample of 5 of its photographs (it does not test the whole folder). "
  "`check_unenrolled_photos.py` re-ran all of them with the Split B checkpoint (face detection, crop, classifier, as the application does).\n")
w(f"- The folder holds {al['photos']} photographs, not 5. The earlier test used a random sample of 5.")
w(f"- Re-run on the 5 sampled photographs: all 5 had a detected face and were all predicted as the same enrolled student, with confidence **{sm['conf_min']:.2f} to {sm['conf_max']:.2f}** "
  f"(exact {sm['conf_min']:.4f} to {sm['conf_max']:.4f}). This matches the 0.89 to 0.93 recorded in `PROMOTION_LOG.md`. All 5 are at or above the 0.60 application threshold.")
w(f"- Re-run on all {al['photos']} photographs: all face-detected, all predicted as that same enrolled student, confidence {al['conf_min']:.4f} to {al['conf_max']:.4f}.")
w(f"- Identity check: {al['byte_identical_to_an_enrolled_photo']} of {al['photos']} photographs are byte-identical (same MD5) to photographs stored under one enrolled student; "
  f"all 5 sampled ones are. ArcFace cosine to the nearest photograph of that enrolled student is {sm['cos_nearest_photo_min']:.4f} to {sm['cos_nearest_photo_max']:.4f} for the 5 sampled photographs "
  f"(and {al['cos_nearest_photo_min']:.3f} to {al['cos_nearest_photo_max']:.3f} over all {al['photos']}). The earlier audits (`diagnosis/DIAGNOSIS.md`, `AUDIT_V3.md`) recorded a class-mean cosine of 0.999.")
w("- **Conclusion: these photographs show an enrolled student (the same photographs stored under a second folder), not a genuinely non-enrolled person. They are not a valid unknown-face test, and the report must not describe them as one.**")
w("- Genuinely non-enrolled face photographs in the repository: **0**. The 29 dataset folders contain only enrolled students, the extra folder above duplicates one of them, and the remaining non-student inputs "
  "in the earlier check were non-face images (interface screenshots, a background patch, flat grey, random noise), whose confidences were 0.09 to 0.20, except random noise at 0.77. "
  "Unknown-face rejection therefore has not been tested.\n")

text = "\n".join(L)
assert not re.search(r"1DA\d\d[A-Z]{2}\d{3}", text), "USN leaked"
(V3 / "REPORT_INPUTS_FINAL.md").write_text(text, encoding="utf-8")
print(text)

