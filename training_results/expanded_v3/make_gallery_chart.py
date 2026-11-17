"""29-student gallery-threshold chart (Split B). Recomputes the sweep for 0.20..0.80 step 0.05
using the same gallery/probe definition as evaluation/evaluate_gallery_29class.py, checks that
counts match the existing JSON where they overlap, and writes the PNG and CSV. Nothing existing is modified."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / "training_results" / "expanded_v3"
OUT = V3 / "graphs_report"
NPZ = ROOT / "data" / "processed" / "facial_pipeline_results_expanded_v3.npz"
JS = ROOT / "evaluation" / "results" / "gallery_threshold_29class_splitB.json"
APP = 0.55
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
                     "axes.labelsize": 8, "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.facecolor": "white", "savefig.transparent": False})

d = np.load(NPZ, allow_pickle=True)
emb, labels, meta = d["embeddings"], np.array([str(x) for x in d["labels"]]), d["metadata"]
rows = {}
for i, m in enumerate(meta):
    m = m.item() if hasattr(m, "item") else m
    if int(m["augmentation_index"]) == 0:
        rows[(m["student_id"], m["source_image"])] = i
sp = json.loads((V3 / "splits_B.json").read_text(encoding="utf-8"))
classes = sp["classes"]
protos = []
for c in classes:
    idx = [rows[(e["usn"], e["source_image"])] for e in sp["train"] if e["usn"] == c]
    e = emb[idx].astype(np.float64)
    e = e / np.linalg.norm(e, axis=1, keepdims=True)
    m = e.mean(0)
    protos.append(m / np.linalg.norm(m))
protos = np.stack(protos)
tidx = [rows[(e["usn"], e["source_image"])] for e in sp["test"]]
tx = emb[tidx].astype(np.float64)
tx = tx / np.linalg.norm(tx, axis=1, keepdims=True)
ty = np.array([classes.index(e["usn"]) for e in sp["test"]])
sim = tx @ protos.T
top, topsim = sim.argmax(1), sim.max(1)
N = len(ty)
assert len(classes) == 29 and N == 138 and len(sp["train"]) == 654

ths = [round(0.20 + 0.05 * k, 2) for k in range(13)]
rec_rows = []
for th in ths:
    a = topsim >= th
    c = int((a & (top == ty)).sum()); w = int((a & (top != ty)).sum()); r = int((~a).sum())
    p = c / (c + w) if c + w else 0.0
    rc = c / N
    f = 2 * p * rc / (p + rc) if p + rc else 0.0
    rec_rows.append(dict(threshold=th, correct=c, wrong=w, rejected=r, precision=round(p, 4),
                         recall=round(rc, 4), f1=round(f, 4), wrong_rate=round(w / N, 4), reject_rate=round(r / N, 4)))
# verify against existing JSON
old = {round(s["threshold"], 2): s for s in json.loads(JS.read_text(encoding="utf-8"))["threshold_sweep"]}
n_match = 0
for r in rec_rows:
    o = old.get(r["threshold"])
    if o:
        assert (o["accepted_correct"], o["accepted_wrong_identity"], o["rejected"]) == (r["correct"], r["wrong"], r["rejected"]), r
        n_match += 1
print("matched thresholds vs JSON:", n_match, "of", len(rec_rows))

with open(OUT / "gallery_threshold_splitB.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rec_rows[0].keys()))
    w.writeheader(); w.writerows(rec_rows)

x = [r["threshold"] for r in rec_rows]
fig, ax = plt.subplots(figsize=(6.3, 3.9))
ax2 = ax.twinx()
l1, = ax.plot(x, [r["precision"] for r in rec_rows], color="#4C72B0", ls="-", marker="o", ms=4, lw=1.4, label="Precision")
l2, = ax.plot(x, [r["recall"] for r in rec_rows], color="#DD8452", ls="--", marker="s", ms=4, lw=1.4, label="Recall")
l3, = ax.plot(x, [r["f1"] for r in rec_rows], color="#55A868", ls="-.", marker="^", ms=4, lw=1.4, label="F1-score")
l4, = ax2.plot(x, [r["wrong_rate"] for r in rec_rows], color="#C44E52", ls=":", marker="D", ms=4, lw=1.4, label="Wrong-identity rate (right axis)")
l5, = ax2.plot(x, [r["reject_rate"] for r in rec_rows], color="#7F7F7F", ls=(0, (5, 1, 1, 1)), marker="v", ms=4, lw=1.4, label="Rejection rate (right axis)")
v = ax.axvline(APP, color="black", ls=":", lw=1.2, label="Application threshold (0.55)")
ax.set_xlim(0.19, 0.81); ax.set_ylim(0, 1.05); ax2.set_ylim(0, 1.05)
ax.set_xticks(x); ax.set_xticklabels([f"{t:.2f}" for t in x], rotation=45)
ax.set_xlabel("Cosine similarity threshold")
ax.set_ylabel("Score"); ax2.set_ylabel("Rate (fraction of 138 probes)")
ax.grid(alpha=0.3)
ax.set_title("Gallery Matching Performance vs Cosine Threshold\n(Split B, 29 Students, 138 Test Photographs)")
ax.legend(handles=[l1, l2, l3, l4, l5, v], loc="lower center", bbox_to_anchor=(0.5, -0.38), ncol=3, frameon=False, fontsize=7)
fig.tight_layout()
fig.savefig(OUT / "gallery_threshold_splitB.png", dpi=300)
print("saved")
for r in rec_rows:
    print(r)
