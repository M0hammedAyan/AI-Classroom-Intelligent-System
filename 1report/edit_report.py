import copy, csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from docx import Document
from docx.shared import Emu, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System"
SRC = ROOT + r"\1report\3Report (1).docx"
OUT = ROOT + r"\1report\3Report (1)_updated.docx"
G = ROOT + r"\training_results\expanded_v3\graphs_report"
FULL = 6120130  # usable text width in EMU (A4, 2 cm margins)

# ---- re-render risk confusion matrix without a baked figure number ----
cm = np.array([[0, 3, 9], [1, 29, 51], [0, 36, 71]])
labels = ["Low", "Medium", "High"]
fig, ax = plt.subplots(figsize=(6.2, 5.4), dpi=300)
im = ax.imshow(cm, cmap="Blues", vmin=0, vmax=80)
for i in range(3):
    for j in range(3):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=18, fontweight="bold",
                color="white" if cm[i, j] > 45 else "#12304d")
ax.set_xticks(range(3)); ax.set_xticklabels(labels)
ax.set_yticks(range(3)); ax.set_yticklabels(labels)
ax.set_xlabel("Predicted risk category"); ax.set_ylabel("Actual risk category")
ax.set_title("Confusion Matrix for XGBoost Academic Risk Classification", fontsize=11)
cb = fig.colorbar(im, ax=ax); cb.set_label("Number of test records")
fig.text(0.5, 0.01, "Synthetic dataset, 200 held-out test records. Correct classifications: 100 / 200 (50.00%)",
         ha="center", fontsize=8)
fig.tight_layout(rect=(0, 0.04, 1, 1))
RISK_CM = G + r"\risk_confusion_matrix_report.png"
fig.savefig(RISK_CM, dpi=300, facecolor="white")
plt.close(fig)

doc = Document(SRC)
body = doc.element.body


def paras():
    return [Paragraph(e, doc) for e in body.iterchildren() if e.tag.endswith('}p')]


def find(prefix=None, contains=None):
    res = [p for p in paras() if (prefix and p.text.startswith(prefix)) or (contains and contains in p.text)]
    assert len(res) == 1, (prefix, contains, len(res))
    return res[0]


def set_text(p, text):
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    return p


def clone(template, text):
    e = copy.deepcopy(template._p)
    p = Paragraph(e, template._parent)
    set_text(p, text)
    return p


T_BODY = find(prefix="The recorded Split B classifier evaluation")
T_CAP = find(prefix="Table 7.3 ResNet-50")
T_EMPTY = Paragraph(T_BODY._p.getnext(), doc)  # empty justified paragraph
T_BODY_E = copy.deepcopy(T_BODY._p)
T_CAP_E = copy.deepcopy(T_CAP._p)
T_EMPTY_E = copy.deepcopy(T_EMPTY._p)


def mk(kind, text=""):
    e = copy.deepcopy({"body": T_BODY_E, "cap": T_CAP_E, "empty": T_EMPTY_E}[kind])
    p = Paragraph(e, doc)
    if kind != "empty":
        set_text(p, text)
    return e


def mk_pic(path, max_h_cm=13.0, width=FULL):
    w, h = Image.open(path).size
    height = width * h / w
    maxh = max_h_cm / 2.54 * 914400
    if height > maxh:
        width = int(width * maxh / height)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Emu(int(width)))
    e = p._p
    e.getparent().remove(e)
    return e


def insert_after(anchor, elems):
    for e in elems:
        anchor.addnext(e)
        anchor = e
    return anchor


def fig_block(lead, path, caption, **kw):
    return [mk("body", lead), mk_pic(path, **kw), mk("cap", caption), mk("empty")]


def drop_picture_par(par):
    rids = [b for b in par._p.xpath('.//a:blip/@r:embed')]
    par._p.getparent().remove(par._p)
    for rid in rids:
        doc.part.drop_rel(rid)


def cell_set(cell, text):
    p = cell.paragraphs[0]
    if p.runs:
        set_text(p, text)
    else:
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)


def table_after(cap_prefix):
    cap = find(prefix=cap_prefix)
    return Table(cap._p.getnext(), doc)


def add_col(tbl):
    grid = tbl._tbl.tblGrid
    gc = grid.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}gridCol')
    grid.append(copy.deepcopy(gc[-1]))
    for tr in tbl._tbl.tr_lst:
        tcs = tr.tc_lst
        tcs[-1].addnext(copy.deepcopy(tcs[-1]))


def add_rows(tbl, n):
    last = tbl._tbl.tr_lst[-1]
    for _ in range(n):
        last.addnext(copy.deepcopy(last))
        last = last.getnext()


def fill(tbl, rows):
    assert len(tbl.rows) == len(rows), (len(tbl.rows), len(rows))
    for r, vals in zip(tbl.rows, rows):
        assert len(r.cells) == len(vals)
        for c, v in zip(r.cells, vals):
            cell_set(c, v)


# ---- Table 7.2 ----
t72 = table_after("Table 7.2 Evaluation Scope")
cell_set(t72.rows[1].cells[1], "95 clean test photographs (Split A, 80:10:10) and 138 clean test photographs "
                               "(Split B, 70:15:15), across 29 identities")
cell_set(t72.rows[2].cells[1], "138 Split B test photographs against a 29-identity gallery built from 654 training photographs")

# ---- 7.5.1 intro ----
p1 = set_text(find(prefix="The recorded Split B classifier evaluation"),
              "The classifier was trained and evaluated on face crops from 29 identity classes. A total of 947 "
              "photographs were audited, 17 were excluded because the face was wrong or could not be detected, and "
              "930 were used. Each photograph contributes one clean face crop and 30 augmented variants, giving "
              "28,830 samples. Between 25 and 41 photographs were used per identity (median 32).")
p1._p.addnext(mk("body",
    "Samples were split by source photograph, so no photograph contributes to more than one of the training, "
    "validation and test sets. Validation and test sets contain only clean (unaugmented) crops. Two splits were "
    "evaluated: Split A (80:10:10) with 740, 95 and 95 photographs (22,940 training samples), and Split B "
    "(70:15:15) with 654, 138 and 138 photographs (20,274 training samples). The model is an ImageNet-pretrained "
    "ResNet-50 with a new 29-way output layer, 112 × 112 input, Adam (learning rate 1e-4), label smoothing 0.1, "
    "class-weighted cross-entropy, early stopping with patience 7, a maximum of 30 epochs and seed 42. The "
    "checkpoint was chosen on validation accuracy only, and the test set was not used for tuning. The Split B "
    "checkpoint is the one used by the application, with an acceptance threshold of 0.60."))

# ---- Table 7.3 ----
t73 = table_after("Table 7.3 ResNet-50")
add_col(t73)
add_rows(t73, 14 - 10)
fill(t73, [
    ["Metric", "Split A (80:10:10)", "Split B (70:15:15)"],
    ["Number of identity classes", "29", "29"],
    ["Training samples", "22,940", "20,274"],
    ["Validation photographs", "95", "138"],
    ["Test photographs", "95", "138"],
    ["Input image size", "112 × 112 pixels", "112 × 112 pixels"],
    ["Epochs completed", "8", "10"],
    ["Selected epoch", "1", "3"],
    ["Best validation accuracy", "100.00%", "99.28%"],
    ["Final training accuracy", "99.94%", "100.00%"],
    ["Test accuracy", "97.89% (93/95)", "99.28% (137/138)"],
    ["Test accuracy 95% Wilson interval", "92.65% to 99.42%", "96.01% to 99.87%"],
    ["Test macro precision", "0.9845", "0.9943"],
    ["Test macro recall", "0.9770", "0.9914"],
    ["Test macro F1-score", "0.9774", "0.9919"],
])

# ---- text after Table 7.3 + classifier figures ----
a = set_text(find(prefix="The test accuracy corresponds to"),
    "Split A classified 93 of 95 test photographs correctly (97.89%) and Split B classified 137 of 138 (99.28%). "
    "In Split A the validation accuracy was 100.00% at every epoch, so validation gave no basis for choosing "
    "between epochs and the first epoch was kept. The test sets are small. Each student has only 3 to 4 (Split A) "
    "or 4 to 6 (Split B) test photographs, so a single photograph changes one student's accuracy by 17 to 33 "
    "percentage points, and the confidence intervals in Table 7.3 are wide.")
b = set_text(find(prefix="The overall result therefore demonstrates"),
    "All misclassified photographs (two in Split A, one in Split B) had a confidence below the application "
    "threshold of 0.60 (0.27 and 0.12 in Split A, 0.33 in Split B). In the application they would therefore be "
    "rejected rather than assigned to another student.")
new = [
    mk("body", "The training loss plateaus near 0.66 in Figure 7.1 because label smoothing of 0.1 sets a floor on "
               "the loss. It does not indicate underfitting."),
    mk("body", "These results demonstrate classifier feasibility on the evaluated closed set of enrolled students. "
               "They do not establish equal reliability for every student or performance on non-enrolled people, "
               "small or occluded faces, or multi-face classroom scenes."),
]
new += fig_block("Figure 7.1 shows training and validation loss and accuracy for Split B. Loss includes label "
                 "smoothing of 0.1.", G + r"\curves_splitB.png",
                 "Fig. 7.1 - Training and Validation Loss and Accuracy (Split B, 70:15:15)")
new += fig_block("Figure 7.2 shows the confusion matrix for the 138 Split B test photographs. One photograph is "
                 "off the diagonal.", G + r"\confusion_splitB.png",
                 "Fig. 7.2 - Confusion Matrix on the Split B Test Photographs")
new += fig_block("Figure 7.3 shows test accuracy for each of the 29 identities, identified only by anonymous "
                 "labels S01 to S29, with the overall test accuracy as a dashed line.",
                 G + r"\per_student_accuracy_splitB.png",
                 "Fig. 7.3 - Per-Student Test Accuracy (Split B)")
insert_after(b._p, new)

# ---- 7.5.2 gallery ----
set_text(find(prefix="The gallery matching evaluation compares"),
    "The gallery matching evaluation compares cosine similarity thresholds from 0.20 to 0.80 on the 29-identity "
    "data. The gallery holds one mean ArcFace embedding per identity, computed from the clean crops of the 654 "
    "Split B training photographs. The probes are the 138 clean Split B test crops. Each probe is matched to its "
    "top-1 gallery identity and accepted only if the cosine similarity is at least the threshold.")
t74 = table_after("Table 7.4 Selected Gallery")
add_col(t74); add_col(t74)
add_rows(t74, 1)
sel = {0.2, 0.3, 0.4, 0.55, 0.7, 0.8}
rows = [["Threshold", "Correct Matches", "Wrong-Identity Matches", "Rejected Samples", "Precision", "Recall", "F1-score"]]
for r in csv.DictReader(open(G + r"\gallery_threshold_splitB.csv")):
    if round(float(r["threshold"]), 2) in sel:
        assert int(r["correct"]) + int(r["wrong"]) + int(r["rejected"]) == 138
        rows.append(["%.2f" % float(r["threshold"]), r["correct"], r["wrong"], r["rejected"],
                     "%.4f" % float(r["precision"]), "%.4f" % float(r["recall"]), "%.4f" % float(r["f1"])])
fill(t74, rows)
set_text(find(prefix="Each row contains 107"),
    "Each row contains 138 evaluated probes. Precision is correct / (correct + wrong-identity), recall is "
    "correct / 138, and F1 is their harmonic mean.")
set_text(find(prefix="The recorded sweep reports"),
    "The highest F1 value, 0.9638, occurs at thresholds 0.20 and 0.25 (133 correct, 5 wrong-identity, 0 "
    "rejected). At the application threshold of 0.55 the precision is 1.0000, the recall is 0.9058 and the F1 "
    "value is 0.9506 (125 correct, 0 wrong-identity, 13 rejected). No wrong-identity match is accepted at any "
    "threshold from 0.50 upward. Without a threshold, the top-1 match is correct for 133 of the 138 probes.")
# replace old gallery chart
old = [p for p in paras() if p._p.xpath('.//a:blip') and p._p.xpath('.//a:blip/@r:embed') and
       'image20' in doc.part.rels[p._p.xpath('.//a:blip/@r:embed')[0]].target_ref]
assert len(old) == 1
anchor = old[0]._p.getprevious()
drop_picture_par(old[0])
insert_after(anchor, [e for e in fig_block(
    "Figure 7.4 plots precision, recall and F1 together with the wrong-identity and rejection rates. The dotted "
    "line marks the application threshold of 0.55.", G + r"\gallery_threshold_splitB.png",
    "Fig. 7.4 - Effect of Cosine Similarity Threshold on Gallery Matching (Split B)")[:3]])

# ---- 7.5.3 ----
set_text(find(prefix="The threshold evaluation labels wrong-identity"),
    "In the threshold evaluation, precision counts only accepted matches, so wrong-identity matches reduce "
    "precision but rejections do not. Recall divides correct matches by all 138 probes, so rejections reduce "
    "recall. The wrong-identity rate is wrong-identity matches divided by all probes. This is not equivalent to "
    "an impostor false acceptance rate measured with non-enrolled people.")
find(prefix="Its reported recall also uses")._p.getparent().remove(find(prefix="Its reported recall also uses")._p)
set_text(find(prefix="Accordingly, these values"), "The counts in Table 7.4 give a direct description of the observed outcomes.")
p = find(prefix="The threshold sweep evaluates gallery matching")
set_text(p, p.text + " All probes are clean single-face crops of enrolled students. Rejection of non-enrolled "
                     "people has not been tested because no such photographs were available.")

# ---- 7.6 risk ----
a = find(contains="predictive usefulness")
insert_after(a._p, fig_block(
    "Figure 7.5 compares the accuracy and macro F1-score of the two models and shows the majority-class "
    "accuracy baseline of 0.535.", G + r"\risk_model_comparison.png",
    "Fig. 7.5 - Accuracy and Macro F1-score of the Academic Risk Models", max_h_cm=10.0))
old = [p for p in paras() if p._p.xpath('.//a:blip/@r:embed') and
       'image21' in doc.part.rels[p._p.xpath('.//a:blip/@r:embed')[0]].target_ref]
assert len(old) == 1
anchor = old[0]._p.getprevious()
drop_picture_par(old[0])
insert_after(anchor, [mk_pic(RISK_CM, max_h_cm=9.0),
                      mk("cap", "Fig. 7.6 - Confusion Matrix for XGBoost Academic Risk Classification")])
x = find(prefix="The earlier advertised F1 value")
x._p.getparent().remove(x._p)

# ---- limitations, summary, conclusion ----
set_text(find(prefix="Recognition datasets contain relatively"),
    "Recognition test sets are small: each identity has only a few test photographs, and the confidence "
    "intervals are wide.")
set_text(find(prefix="Dedicated impostor and presentation-attack"),
    "Test crops are clean single-face crops of enrolled students (closed set). Non-enrolled faces, small "
    "back-row faces, occlusion and multi-face classroom scenes were not evaluated, and rejection of non-enrolled "
    "people has not been tested. Dedicated impostor and presentation-attack testing is insufficient to "
    "establish biometric security.")
p = find(prefix="Academic prediction uses synthetic data")
set_text(p, p.text + " The risk model is trained and tested on synthetic data and does not exceed the "
                     "majority-class baseline.")
set_text(find(prefix="The recorded face-classifier evaluation reports"),
    "The face-classifier evaluation covers 29 identities. Split A reached 97.89% test accuracy on 95 photographs "
    "and Split B reached 99.28% on 138 photographs, with small test sets and wide confidence intervals. In the "
    "gallery threshold experiment, no wrong-identity match is accepted from a threshold of 0.50 upward, at the "
    "cost of rejecting more enrolled students as the threshold rises.")
set_text(find(prefix="The recorded evaluation demonstrates useful"),
    "The recorded evaluation demonstrates useful capabilities while identifying important limitations. The "
    "ResNet-50 classifier reached 99.28% test accuracy (137 of 138 photographs) on 29 identities in the "
    "configuration used by the application, evaluated on a small closed set of clean face crops. The "
    "gallery-matching experiment showed that increasing the cosine similarity threshold removed wrong-identity "
    "matches while increasing rejection of enrolled students. These findings highlight the need to calibrate "
    "recognition thresholds using representative classroom data.")

doc.save(OUT)
print("saved", OUT)
