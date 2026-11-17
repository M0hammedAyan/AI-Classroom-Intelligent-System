import docx
out = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report\3Report (1)_updated.docx"
d = docx.Document(out)
for t in d.tables:
    if len(t.rows[0].cells)>1 and t.rows[0].cells[1].text.strip() == "Predicted Low":
        for r in t.rows[:-1]:
            for c in r.cells:
                for p in c.paragraphs:
                    p.paragraph_format.keep_with_next = True
        print("fixed 7.7")
d.save(out)
