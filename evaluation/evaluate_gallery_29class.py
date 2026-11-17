"""Gallery threshold sweep on the 29-student data (Split B).

Gallery: per-student mean of the L2-normalised ArcFace embeddings of the clean crops
(augmentation_index 0) of that student's Split B TRAINING photos only, re-normalised.
Probes: the Split B TEST clean crops. Top-1 cosine match against the 29 prototypes.
Database embeddings are NOT used (they were enrolled from all photos and would leak test photos).

Metric definitions (same as evaluation/evaluate_recognition.py):
  tp = accepted and correct; fp = accepted and wrong identity; fn = rejected (top-1 below threshold)
  accuracy = tp / total; precision = tp / (tp + fp);
  recall_original = tp / (tp + fn)   (as in evaluate_recognition.py; wrong-identity accepts are not in the denominator)
  F1_original = harmonic mean of precision and recall_original
Additional definitions requested for the report:
  recall = tp / total probes (equals accuracy); F1 = harmonic mean of precision and this recall.
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "training_results" / "expanded_v3"
NPZ = ROOT / "data" / "processed" / "facial_pipeline_results_expanded_v3.npz"
OUT = ROOT / "evaluation" / "results" / "gallery_threshold_29class_splitB.json"
APP_THRESHOLD = 0.55
# Table 7.4 thresholds plus 0.20 to 0.70 in steps of 0.05
THRESHOLDS = sorted({0.30, 0.40, 0.55, 0.70, 0.80} | {round(0.20 + 0.05 * k, 2) for k in range(11)})


def f1(p, r):
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


d = np.load(NPZ, allow_pickle=True)
emb, labels, meta = d["embeddings"], np.array([str(x) for x in d["labels"]]), d["metadata"]
rows = {}
for i, m in enumerate(meta):
    m = m.item() if hasattr(m, "item") else m
    if int(m["augmentation_index"]) == 0:
        rows[(m["student_id"], m["source_image"])] = i
sp = json.loads((V3 / "splits_B.json").read_text(encoding="utf-8"))
classes = sp["classes"]
assert not ({(e["usn"], e["source_image"]) for e in sp["train"]} & {(e["usn"], e["source_image"]) for e in sp["test"]})

protos = []
for c in classes:
    idx = [rows[(e["usn"], e["source_image"])] for e in sp["train"] if e["usn"] == c]
    assert idx and all(labels[i] == c for i in idx)
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
top = sim.argmax(1)
topsim = sim.max(1)
total = len(ty)
print("students:", len(classes), "probes:", total, "top-1 (no threshold) correct:", int((top == ty).sum()))

sweep = []
for th in THRESHOLDS:
    acc_mask = topsim >= th
    tp = int((acc_mask & (top == ty)).sum())
    fp = int((acc_mask & (top != ty)).sum())
    fn = int((~acc_mask).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / total
    rec_o = tp / (tp + fn) if tp + fn else 0.0
    sweep.append({"threshold": th, "accepted_correct": tp, "accepted_wrong_identity": fp, "rejected": fn,
                  "total": total, "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1(prec, rec), 4),
                  "accuracy": round(tp / total, 4), "recall_original_definition": round(rec_o, 4),
                  "f1_original_definition": round(f1(prec, rec_o), 4),
                  "_f1_raw": f1(prec, rec), "_f1o_raw": f1(prec, rec_o)})
best = max(s["_f1_raw"] for s in sweep)
best_o = max(s["_f1o_raw"] for s in sweep)
best_th = [s["threshold"] for s in sweep if abs(s["_f1_raw"] - best) < 1e-12]
best_th_o = [s["threshold"] for s in sweep if abs(s["_f1o_raw"] - best_o) < 1e-12]
for s in sweep:
    s.pop("_f1_raw"); s.pop("_f1o_raw")
out = {"split": "B (70:15:15)", "num_students": len(classes), "total_probe_samples": total,
       "gallery_source": "per-student mean of L2-normalised clean-crop embeddings of Split B training photos only",
       "gallery_photos": len(sp["train"]), "probes": "Split B test clean crops",
       "top1_correct_without_threshold": int((top == ty).sum()),
       "best_f1": round(best, 4), "best_f1_thresholds": best_th,
       "best_f1_original_definition": round(best_o, 4), "best_f1_original_definition_thresholds": best_th_o,
       "application_threshold": APP_THRESHOLD,
       "at_application_threshold": next(s for s in sweep if s["threshold"] == APP_THRESHOLD),
       "top1_similarity_correct_min": float(topsim[top == ty].min()),
       "top1_similarity_wrong": [float(x) for x in topsim[top != ty]],
       "threshold_sweep": sweep}
OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
for s in sweep:
    print(s)
print("best F1", best, best_th, "| original-definition best", best_o, best_th_o)
