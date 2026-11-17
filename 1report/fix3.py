import docx
out = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report\3Report (1)_updated.docx"
d = docx.Document(out)
for p in d.paragraphs:
    if p.text.strip().startswith("Table 7.7"):
        p.paragraph_format.keep_with_next = True; print("cap")
d.save(out)
