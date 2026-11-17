import fitz
base = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report"
d = fitz.open(base + r"\3Report (1)_updated.pdf")
pgs = [i for i, p in enumerate(d) if i > 60 and ("Fig. 7." in p.get_text() or "Figure 7." in p.get_text())]
print([i + 1 for i in pgs])
pix = [d[i].get_pixmap(dpi=50) for i in pgs]
w, h = pix[0].width, pix[0].height
out = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, w * len(pix), h), False)
out.clear_with(255)
for k, p in enumerate(pix):
    p.set_origin(k * w, 0)
    out.copy(p, p.irect)
out.save(base + r"\_render\m3.png")
