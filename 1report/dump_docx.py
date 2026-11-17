import sys, re, zipfile
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
p = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report\3Report (1).docx"
d = Document(p)
rels = {r.rId: r.target_ref for r in d.part.rels.values()}
out = []
body = d.element.body
i = 0
for ch in body.iterchildren():
    tag = ch.tag.split('}')[1]
    if tag == 'p':
        para = Paragraph(ch, d)
        xml = ch.xml
        imgs = re.findall(r'r:embed="(rId\d+)"', xml)
        instr = re.findall(r'<w:instrText[^>]*>([^<]*)<', xml)
        pf = para.paragraph_format
        runs = para.runs
        f = ''
        if runs:
            r0 = runs[0]
            f = f"{r0.font.name},{r0.font.size.pt if r0.font.size else None},b={r0.bold}"
        out.append(f"[{i}] P style={para.style.name} al={para.alignment} {f} imgs={[rels.get(x) for x in imgs]} fld={instr}: {para.text}")
    elif tag == 'tbl':
        t = Table(ch, d)
        out.append(f"[{i}] TABLE style={t.style.name if t.style else None} {len(t.rows)}x{len(t.columns)}")
        for r in t.rows:
            out.append("    | " + " | ".join(c.text.replace('\n', ' / ') for c in r.cells))
    else:
        out.append(f"[{i}] {tag}")
    i += 1
open(r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report\_dump.txt", "w", encoding="utf-8").write("\n".join(out))
print(len(out))
z = zipfile.ZipFile(p)
for n in z.namelist():
    if 'media' in n:
        print(n, z.getinfo(n).file_size)
