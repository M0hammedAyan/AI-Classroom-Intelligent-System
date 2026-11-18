from pathlib import Path
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

SRC = Path(__file__).resolve().parent / "graphs_report"
OUT = SRC / "VISTA_report_graphs.pdf"

TITLES = {
    "curves_splitB": "Training and Validation Loss and Accuracy (Split B, 70:15:15)",
    "curves_splitA": "Training and Validation Loss and Accuracy (Split A, 80:10:10)",
    "confusion_splitB": "Test Confusion Matrix (Split B, 138 test photographs)",
    "confusion_splitA": "Test Confusion Matrix (Split A, 95 test photographs)",
    "per_student_accuracy_splitB": "Per-Student Test Accuracy (Split B)",
    "per_student_accuracy_splitA": "Per-Student Test Accuracy (Split A)",
    "gallery_threshold_splitB": "Gallery Matching Performance vs Cosine Threshold (Split B, 29 identities, 138 probes)",
    "risk_model_comparison": "Academic Risk Model Comparison on the Held-Out Test Set (n = 200)",
}
TITLES_ORDERED = TITLES
ORDER = [
    "curves_splitB", "confusion_splitB", "per_student_accuracy_splitB",
    "curves_splitA", "confusion_splitA", "per_student_accuracy_splitA",
    "gallery_threshold_splitB", "risk_model_comparison",
]

found = {p.stem: p for p in SRC.glob("*.png") if not p.name.startswith("_")}
stems = [s for s in ORDER if s in found] + sorted(s for s in found if s not in ORDER)
figs = []
for s in stems:
    title = TITLES.get(s, s.replace("_", " ").title())
    figs.append((s, title, found[s]))

W, H = A4
M = 1.5 * cm
c = canvas.Canvas(str(OUT), pagesize=A4)
c.setTitle("VISTA - Report Graphs")

# cover
c.setFont("Helvetica-Bold", 26)
c.drawCentredString(W / 2, H - 6 * cm, "VISTA - Report Graphs")
c.setFont("Helvetica", 11)
c.drawCentredString(W / 2, H - 7.2 * cm, "Face-recognition graphs use anonymous identity labels S01-S29.")
c.drawCentredString(W / 2, H - 8 * cm, "2026")
y = H - 10 * cm
c.setFont("Helvetica", 10)
for i, (_, t, _) in enumerate(figs, 1):
    c.drawString(3 * cm, y, f"{i}. Figure {i}: {t}")
    y -= 0.8 * cm
c.showPage()

for i, (_, t, p) in enumerate(figs, 1):
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M, H - M - 11, f"Figure {i}: {t}")
    top = H - M - 1.0 * cm
    aw, ah = W - 2 * M, top - M
    with Image.open(p) as im:
        iw, ih = im.size
        im = im.convert("RGB")
        ir = ImageReader(im)
    sc = min(aw / iw, ah / ih)
    w, h = iw * sc, ih * sc
    c.drawImage(ir, (W - w) / 2, top - h, w, h)
    c.showPage()
c.save()
print("Included:")
for i, (s, t, p) in enumerate(figs, 1):
    print(i, p.name)
