import fitz, re, os
base = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report"
d = fitz.open(base + r"\3Report (1)_updated.pdf")
os.makedirs(base + r"\_render", exist_ok=True)
keys = ["Fig. 7.", "Table 7.3", "Table 7.4", "Table 7.5", "Table 7.2"]
pages = []
for i, p in enumerate(d):
    t = p.get_text()
    if any(k in t for k in keys) and i > 40:
        pages.append(i)
print(pages)
for i in pages:
    d[i].get_pixmap(dpi=60).save(base + r"\_render\p%d.png" % (i + 1))
