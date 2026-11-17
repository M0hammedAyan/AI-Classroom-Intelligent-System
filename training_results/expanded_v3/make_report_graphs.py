"""Anonymised report graphs for the final 29-student classifier.

Recomputes test predictions from the checkpoints, checks them against eval_results.json,
writes 6 PNGs (300 dpi, white) plus per-epoch CSVs and an anonymised results JSON into
training_results/expanded_v3/graphs_report/. The USN -> S01..S29 mapping is written only to
USN_to_ID_PRIVATE.csv (git-ignored). Existing files are not modified.
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from train_expanded_v3 import ResNet50FaceClassifier, IMG_SIZE  # noqa: E402

V3 = ROOT / "training_results" / "expanded_v3"
OUT = V3 / "graphs_report"
OUT.mkdir(exist_ok=True)
NPZ = ROOT / "data" / "processed" / "facial_pipeline_results_expanded_v3.npz"

SPLIT_TITLE = {"A": "Split A, 80:10:10", "B": "Split B, 70:15:15"}
BAR_COLOUR = "#4C72B0"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
                     "axes.labelsize": 8, "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.facecolor": "white", "savefig.transparent": False})

ev = json.loads((V3 / "eval_results.json").read_text(encoding="utf-8"))

# ---- fixed anonymous mapping (sorted USN) ----
usns = sorted(ev["A"]["class_names"])
assert usns == sorted(ev["B"]["class_names"]) and len(usns) == 29
ID = {u: f"S{i + 1:02d}" for i, u in enumerate(usns)}
with open(OUT / "USN_to_ID_PRIVATE.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["usn", "id"])
    for u in usns:
        w.writerow([u, ID[u]])
ids = [ID[u] for u in usns]

# ---- recompute predictions from checkpoints ----
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
d = np.load(NPZ, allow_pickle=True)
images, meta = d["images"], d["metadata"]
rows = {}
for i, m in enumerate(meta):
    m = m.item() if hasattr(m, "item") else m
    if int(m["augmentation_index"]) == 0:
        rows[(m["student_id"], m["source_image"])] = i
norm = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])

res = {}
for s in "AB":
    sp = json.loads((V3 / f"splits_{s}.json").read_text(encoding="utf-8"))
    classes = sp["classes"]
    assert classes == usns
    ci = {c: i for i, c in enumerate(classes)}
    ck = torch.load(V3 / f"best_model_expanded_v3_split{s}.pth", map_location="cpu", weights_only=False)
    assert ck["class_names"] == classes
    model = ResNet50FaceClassifier(len(classes))
    model.load_state_dict(ck["model_state_dict"])
    model.to(dev).eval()
    idx = [rows[(e["usn"], e["source_image"])] for e in sp["test"]]
    y = np.array([ci[e["usn"]] for e in sp["test"]])
    preds, confs = [], []
    with torch.no_grad():
        for b in range(0, len(idx), 32):
            x = torch.stack([norm(Image.fromarray(images[i]).resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR))
                             for i in idx[b:b + 32]]).to(dev)
            pr = torch.softmax(model(x), 1)
            c, p = pr.max(1)
            preds += p.cpu().tolist()
            confs += c.cpu().tolist()
    p = np.array(preds)
    cm = np.zeros((29, 29), int)
    for t, q in zip(y, p):
        cm[t, q] += 1
    # verify against eval_results.json
    e = ev[s]
    assert cm.tolist() == e["confusion_matrix"], f"confusion mismatch split {s}"
    assert int((y == p).sum()) == e["overall"]["correct"] and len(y) == e["overall"]["n"]
    for i, c in enumerate(classes):
        assert (int(cm[i, i]), int(cm[i].sum())) == (e["per_class"][c]["correct"], e["per_class"][c]["n"])
    mis = [{"true": ID[classes[y[j]]], "pred": ID[classes[p[j]]], "confidence": float(confs[j])}
           for j in range(len(y)) if y[j] != p[j]]
    assert len(mis) == len(e["misclassified"])
    res[s] = {"cm": cm, "n": len(y), "correct": int((y == p).sum()),
              "per_class": {ID[c]: (int(cm[i, i]), int(cm[i].sum())) for i, c in enumerate(classes)},
              "mis": mis, "ckpt_epoch": ck["epoch"],
              "correct_conf_min": float(min(c for c, a, b in zip(confs, y, p) if a == b))}
    print(f"Split {s}: {res[s]['correct']}/{res[s]['n']} matches eval_results.json (confusion, per-class, overall)")

# ---- per-epoch CSVs ----
for s in "AB":
    h = json.loads((V3 / f"history_split{s}.json").read_text(encoding="utf-8"))
    with open(OUT / f"epochs_split{s}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["epoch", "train_loss", "train_acc", "val_loss", "val_acc"])
        for k in range(len(h["train_loss"])):
            w.writerow([k + 1] + [f"{h[c][k]:.4f}" for c in ("train_loss", "train_acc", "val_loss", "val_acc")])

# ---- graphs ----
for s in "AB":
    h = json.loads((V3 / f"history_split{s}.json").read_text(encoding="utf-8"))
    ep = np.arange(1, len(h["train_loss"]) + 1)
    be = ev[s]["checkpoint_epoch"]
    assert be == res[s]["ckpt_epoch"]
    fig, ax = plt.subplots(1, 2, figsize=(6.3, 3.0))
    for a, (tr, va, yl) in zip(ax, (("train_loss", "val_loss", "Loss (with label smoothing 0.1)"),
                                    ("train_acc", "val_acc", "Accuracy"))):
        a.plot(ep, h[tr], "o-", ms=3, lw=1.2, label="Training")
        a.plot(ep, h[va], "s-", ms=3, lw=1.2, label="Validation")
        a.axvline(be, color="gray", ls="--", lw=1, label=f"Selected checkpoint (epoch {be})")
        a.set_xlabel("Epoch"); a.set_ylabel(yl)
        a.set_xticks(ep); a.grid(alpha=0.25)
        a.legend(fontsize=6.5, loc="best")
    ax[0].set_title("Loss", fontsize=8.5); ax[1].set_title("Accuracy", fontsize=8.5)
    fig.suptitle(f"Training and Validation Loss and Accuracy ({SPLIT_TITLE[s]})", fontsize=9.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / f"curves_split{s}.png", dpi=300, facecolor="white", transparent=False)
    plt.close(fig)

    cm = res[s]["cm"]
    fig, ax = plt.subplots(figsize=(6.5, 6.0))
    im = ax.imshow(cm, cmap="Blues", vmin=0)
    ax.set_xticks(range(29)); ax.set_yticks(range(29))
    ax.set_xticklabels(ids, rotation=90, fontsize=6); ax.set_yticklabels(ids, fontsize=6)
    for i in range(29):
        for j in range(29):
            if cm[i, j]:
                ax.text(j, i, int(cm[i, j]), ha="center", va="center", fontsize=5.5,
                        color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set_xlabel("Predicted student"); ax.set_ylabel("True student")
    ax.set_title(f"Test Confusion Matrix ({SPLIT_TITLE[s].split(',')[0]}, {res[s]['n']} test photographs)", fontsize=9.5)
    cb = fig.colorbar(im, fraction=0.046, pad=0.02); cb.ax.tick_params(labelsize=6)
    cb.set_label("Number of photographs", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / f"confusion_split{s}.png", dpi=300, facecolor="white", transparent=False)
    plt.close(fig)

    pc = res[s]["per_class"]
    acc = [pc[i][0] / pc[i][1] for i in ids]
    overall = res[s]["correct"] / res[s]["n"]
    assert abs(overall - ev[s]["overall"]["accuracy"]) < 1e-12
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    ax.bar(range(29), acc, color=BAR_COLOUR, width=0.75)
    for k, i in enumerate(ids):
        ax.text(k, acc[k] + 0.006, f"{pc[i][0]}/{pc[i][1]}", ha="center", va="bottom", fontsize=5.5)
    ax.axhline(overall, color="black", ls="--", lw=1, label=f"Overall test accuracy {overall * 100:.2f}%")
    ax.set_xticks(range(29)); ax.set_xticklabels(ids, rotation=90, fontsize=6.5)
    ax.set_xlim(-0.7, 28.7); ax.set_ylim(0, 1.05)
    ax.set_xlabel("Student"); ax.set_ylabel("Test accuracy")
    ax.set_title(f"Per-Student Test Accuracy ({SPLIT_TITLE[s]})", fontsize=9.5, loc="left")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / f"per_student_accuracy_split{s}.png", dpi=300, facecolor="white", transparent=False)
    plt.close(fig)

# anonymised computed results for the report-inputs generator (no USNs)
(OUT / "report_results_anonymised.json").write_text(json.dumps(
    {s: {"n": res[s]["n"], "correct": res[s]["correct"], "per_class": res[s]["per_class"],
         "mis": res[s]["mis"], "ckpt_epoch": res[s]["ckpt_epoch"],
         "correct_conf_min": res[s]["correct_conf_min"]} for s in "AB"}, indent=1), encoding="utf-8")
print("done")
