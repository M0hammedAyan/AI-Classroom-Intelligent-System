import re
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
p = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report\3Report (1).docx"
d = Document(p)
ch = list(d.element.body.iterchildren())
def show(i):
    e = ch[i]
    print("=== idx", i, e.tag.split('}')[1])
    x = e.xml
    if e.tag.endswith('}p'):
        print(re.sub(r'xmlns:\w+="[^"]+"\s*', '', x)[:2500])
    else:
        t = Table(e, d)
        print("tblPr:", re.sub(r'xmlns:\w+="[^"]+"\s*', '', t._tbl.tblPr.xml)[:1500])
        print("grid:", [g.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w') for g in t._tbl.tblGrid])
        for ri in (0, 1):
            c = t.rows[ri].cells[0]
            print("row", ri, re.sub(r'xmlns:\w+="[^"]+"\s*', '', t.rows[ri]._tr.xml)[:3000])
for i in (981, 982, 996, 1030, 1013, 1024):
    show(i)
# extents of images
for i in (344, 409, 822, 844, 996, 1030, 1068):
    m = re.findall(r'<wp:(inline|anchor)|<wp:extent cx="(\d+)" cy="(\d+)"', ch[i].xml)
    print(i, m)
sec = ch[-1]
print(re.sub(r'xmlns:\w+="[^"]+"\s*', '', sec.xml)[:800])
