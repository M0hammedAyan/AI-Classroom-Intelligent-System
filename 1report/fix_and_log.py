import re, difflib, docx
base = r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report"
out = base + r"\3Report (1)_updated.docx"
inp = base + r"\3Report (1).docx"
d = docx.Document(out)
n = 0
for p in d.paragraphs:
    if re.match(r"Figure 7\.\d (shows|plots|compares)", p.text.strip()):
        p.paragraph_format.keep_with_next = True
        n += 1
    elif re.match(r"Fig\. 7\.\d - ", p.text.strip()):
        pass
d.save(out)
print("keep_with_next set on", n)

def ptexts(path):
    dd = docx.Document(path)
    return [p.text.strip() for p in dd.paragraphs if p.text.strip()], dd
a, da = ptexts(inp)
b, db = ptexts(out)
L = ["# Report Update Changelog", "",
     "Input: `3Report (1).docx` (unchanged). Output: `3Report (1)_updated.docx` (PDF: `3Report (1)_updated.pdf`).", "",
     "## Figures", "",
     "| Figure | Caption | Status |", "|---|---|---|",
     "| Fig. 7.1 | Training and Validation Loss and Accuracy (Split B, 70:15:15) | added |",
     "| Fig. 7.2 | Confusion Matrix on the Split B Test Photographs | added |",
     "| Fig. 7.3 | Per-Student Test Accuracy (Split B) | added |",
     "| Fig. 7.4 | Effect of Cosine Similarity Threshold on Gallery Matching (Split B) | replaces old gallery threshold chart (old chart removed) |",
     "| Fig. 7.5 | Accuracy and Macro F1-score of the Academic Risk Models | added |",
     "| Fig. 7.6 | Confusion Matrix for XGBoost Academic Risk Classification | re-rendered from the same counts, old number baked into image title removed |",
     "", "Counts: inline images 20 before, 24 after. Figure captions (Fig. x.y) 9 before, 15 after. Tables 27 before and after; table captions 24 before and after (Table numbers 7.1 to 7.12 unchanged).", "",
     "## Tables changed", "",
     "- Table 7.2 (Evaluation Scope): classifier and gallery rows.",
     "- Table 7.3: rewritten as Split A vs Split B (15 rows x 3 columns).",
     "- Table 7.4: rewritten, 7 columns, thresholds 0.20, 0.30, 0.40, 0.55, 0.70, 0.80.",
     "- Tables 7.5 to 7.7: already matched current results, unchanged.", "",
     "## Paragraph changes (old text -> new text)", ""]
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal": continue
    L.append("### %s (old paragraphs %d-%d, new %d-%d)" % (tag, i1, i2, j1, j2))
    nearest = ""
    for k in range(min(i1, len(a)) - 1, -1, -1):
        if re.match(r"^\d+(\.\d+)*\s+[A-Z]", a[k]) and len(a[k]) < 80:
            nearest = a[k]; break
    L.append("Section: " + nearest); L.append("")
    for t in a[i1:i2]: L.append("- OLD: " + t)
    for t in b[j1:j2]: L.append("- NEW: " + t)
    L.append("")
# table cell diffs
def tab(dd, i):
    return [[c.text.strip() for c in r.cells] for r in dd.tables[i].rows]
L.append("## Table content (new)"); L.append("")
for i in range(len(db.tables)):
    if tab(db, i) != tab(da, i):
        L.append("### Table index %d changed" % i)
        L.append("OLD:"); L += ["    " + " | ".join(r) for r in tab(da, i)]
        L.append("NEW:"); L += ["    " + " | ".join(r) for r in tab(db, i)]
        L.append("")
L += ["## Not changed / out of scope", "",
      "- Section 7.5.4 Pilot Evidence still begins 'Earlier project documentation reports...' (out of scope).",
      "- Team table (names) outside the scope was left as is.",
      "- Remaining '107' occurrences are correct: High-class row in Table 7.6 and 107 of 200 majority class.",
      "- The document has no List of Figures/Tables or TOC fields; captions are plain text."]
open(base + r"\CHANGELOG_REPORT_UPDATE.md", "w", encoding="utf8").write("\n".join(L))
