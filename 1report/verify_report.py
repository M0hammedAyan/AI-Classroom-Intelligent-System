import re, sys, docx
from docx.oxml.ns import qn
base = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System"
out = base + r"\1report\3Report (1)_updated.docx"
inp = base + r"\1report\3Report (1).docx"
names = []
for l in open(base + r"\vista\frontend\src\App.jsx", encoding="utf8"):
    m = re.match(r"^([A-Za-z .'-]+)\|(1DA\w+)\s*$", l)
    if m: names.append(m.group(1).strip())

def texts(path):
    d = docx.Document(path)
    items = []
    for i, p in enumerate(d.paragraphs):
        items.append(("P%d" % i, p.text))
    for ti, t in enumerate(d.tables):
        for r, row in enumerate(t.rows):
            for c, cell in enumerate(row.cells):
                items.append(("T%d r%d c%d" % (ti, r, c), cell.text))
    for s in d.sections:
        for p in s.header.paragraphs + s.footer.paragraphs:
            items.append(("HF", p.text))
    return d, items

d, items = texts(out)
pats = [r"1DA\d\d[A-Z]{2}\d{3}", r"v3", r"20 classes", r"20 identities", r"107", r"90\.10", r"0\.957", r"98\.6", r"93\.1", r"duplicate", r"earlier model", r"baseline_before", r"Earlier project"]
for n in names:
    pats.append(re.escape(n))
print("names loaded", len(names))
for loc, t in items:
    for p in pats:
        if re.search(p, t, re.I if p not in ("v3",) else 0):
            print("HIT", loc, p, "|", t[:160].replace("\n", " "))
def counts(path):
    d = docx.Document(path)
    txt = [p.text for p in d.paragraphs]
    fig = [t for t in txt if re.match(r"\s*Fig(ure)?\.?\s*\d", t)]
    tab = [t for t in txt if re.match(r"\s*Table\s*\d+(\.\d+)*\s*[:\-–.]", t)]
    imgs = len(d.inline_shapes)
    return len(d.tables), imgs, fig, tab
for lab, p in (("INPUT", inp), ("OUTPUT", out)):
    nt, ni, fig, tab = counts(p)
    print(lab, "tables", nt, "inline images", ni, "fig captions", len(fig), "table captions", len(tab))
    for f in fig: print("  ", f[:110])
    for f in tab: print("  ", f[:110])
