"""Graphs for v3 results + comparison vs baseline_before_expansion and expanded_v1_failed.
Reads only existing result files; writes PNGs to training_results/expanded_v3/graphs/."""
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

TR = Path(__file__).resolve().parents[1]
V3 = TR / "expanded_v3"
BASE = TR / "baseline_before_expansion"
V1 = TR / "expanded_v1_failed"
G = V3 / "graphs"
G.mkdir(exist_ok=True)

ev = json.loads((V3 / "eval_results.json").read_text(encoding="utf-8"))
hist = {s: json.loads((V3 / f"history_split{s}.json").read_text(encoding="utf-8")) for s in "AB"}
v1h = {s: json.loads((V1 / f"history_expanded_split{s}.json").read_text(encoding="utf-8")) for s in "AB"}


def parse_baseline(split):
    txt = (BASE / f"results_npz_split{split}.txt").read_text(encoding="utf-8", errors="replace")
    ep = re.findall(r"Epoch (\d+):\s+([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+)", txt)
    h = {k: [float(e[i + 1]) for e in ep] for i, k in enumerate(["train_loss", "train_acc", "val_loss", "val_acc"])}
    pc = {m[0]: (int(m[1]), int(m[2])) for m in re.findall(r"(1DA\w+) \(class \d+\): (\d+)/(\d+) =", txt)}
    test = float(re.search(r"Test accuracy\s+: ([\d.]+)%", txt).group(1))
    return h, pc, test


bh, bpc, btest = {}, {}, {}
for s in "AB":
    bh[s], bpc[s], btest[s] = parse_baseline(s)


# 1. loss / accuracy curves
for s in "AB":
    h = hist[s]
    ep = range(1, len(h["train_loss"]) + 1)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(ep, h["train_loss"], "o-", label="train"); ax[0].plot(ep, h["val_loss"], "s-", label="val")
    ax[0].set_title(f"v3 Split {s}: loss (label-smoothed, class-weighted)"); ax[0].set_xlabel("epoch"); ax[0].legend()
    ax[1].plot(ep, h["train_acc"], "o-", label="train"); ax[1].plot(ep, h["val_acc"], "s-", label="val")
    be = ev[s]["checkpoint_epoch"]
    ax[1].axvline(be, color="gray", ls="--", label=f"kept checkpoint (epoch {be})")
    ax[1].set_title(f"v3 Split {s}: accuracy"); ax[1].set_xlabel("epoch"); ax[1].legend()
    fig.tight_layout(); fig.savefig(G / f"v3_curves_split{s}.png", dpi=130); plt.close(fig)

# 2. confusion matrices
for s in "AB":
    r = ev[s]
    cm = np.array(r["confusion_matrix"]); names = r["class_names"]
    fig, ax = plt.subplots(figsize=(11, 9.5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(names))); ax.set_yticks(range(len(names)))
    ax.set_xticklabels(names, rotation=90, fontsize=7); ax.set_yticklabels(names, fontsize=7)
    for i in range(len(names)):
        for j in range(len(names)):
            if cm[i, j]:
                ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=7,
                        color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set_xlabel("predicted"); ax.set_ylabel("true")
    ax.set_title(f"v3 Split {s} test confusion matrix (n={r['n_test']}, acc={r['overall']['accuracy']:.4f})")
    fig.colorbar(im, fraction=0.03); fig.tight_layout()
    fig.savefig(G / f"v3_confusion_split{s}.png", dpi=130); plt.close(fig)

# 3. per-class accuracy bars
for s in "AB":
    r = ev[s]; names = r["class_names"]
    acc = [r["per_class"][c]["accuracy"] for c in names]
    cols = ["tab:orange" if c.startswith("1DA25AI") else "tab:blue" for c in names]
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.bar(range(len(names)), acc, color=cols)
    for i, c in enumerate(names):
        ax.text(i, acc[i] + 0.01, f"{r['per_class'][c]['correct']}/{r['per_class'][c]['n']}", ha="center", fontsize=7)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=90, fontsize=8)
    ax.set_ylim(0, 1.1); ax.set_ylabel("test accuracy")
    ax.set_title(f"v3 Split {s} per-class test accuracy (blue = original 19, orange = new 1DA25AI*)")
    fig.tight_layout(); fig.savefig(G / f"v3_per_class_accuracy_split{s}.png", dpi=130); plt.close(fig)

# 4. comparison vs baseline (Split B and A)
for s in "AB":
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
    for a, key, t in ((ax[0], "val_acc", "validation accuracy"), (ax[1], "val_loss", "validation loss"),
                      (ax[2], "train_acc", "train accuracy")):
        a.plot(range(1, len(bh[s][key]) + 1), bh[s][key], "o-", label="baseline (20 classes)")
        a.plot(range(1, len(hist[s][key]) + 1), hist[s][key], "s-", label="v3 (29 classes)")
        a.plot(range(1, len(v1h[s][key]) + 1), v1h[s][key], "^-", label="v1 failed (32 mislabelled)")
        a.set_title(f"Split {s}: {t}"); a.set_xlabel("epoch"); a.legend(fontsize=8)
    fig.suptitle("Curves are not directly comparable: different class counts and val sets")
    fig.tight_layout(); fig.savefig(G / f"compare_curves_split{s}.png", dpi=130); plt.close(fig)

# 5. test accuracy bars: baseline vs v3 (overall, original students)
labels, vals, cols = [], [], []
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
for a, s in zip(ax, "AB"):
    pc = bpc[s]
    k_all = sum(v[0] for v in pc.values()); n_all = sum(v[1] for v in pc.values())
    orig = {c: v for c, v in pc.items() if c != "1DA22AI402"}  # 1DA22AI402 is not in v3
    k_o = sum(v[0] for v in orig.values()); n_o = sum(v[1] for v in orig.values())
    bars = [
        (f"baseline\n20 cls\n({k_all}/{n_all})", k_all / n_all, "tab:gray"),
        (f"baseline\n19 shared cls\n({k_o}/{n_o})", k_o / n_o, "silver"),
        (f"v3 original 19\n({ev[s]['original_19']['correct']}/{ev[s]['original_19']['n']})", ev[s]["original_19"]["accuracy"], "tab:blue"),
        (f"v3 new 10\n({ev[s]['new_10']['correct']}/{ev[s]['new_10']['n']})", ev[s]["new_10"]["accuracy"], "tab:orange"),
        (f"v3 overall 29\n({ev[s]['overall']['correct']}/{ev[s]['overall']['n']})", ev[s]["overall"]["accuracy"], "tab:green"),
    ]
    a.bar(range(len(bars)), [b[1] for b in bars], color=[b[2] for b in bars])
    for i, b in enumerate(bars):
        a.text(i, b[1] + 0.01, f"{b[1]*100:.1f}%", ha="center", fontsize=9)
    a.set_xticks(range(len(bars))); a.set_xticklabels([b[0] for b in bars], fontsize=8)
    a.set_ylim(0, 1.1); a.set_title(f"Split {s} test accuracy")
fig.suptitle("Baseline vs v3 test accuracy (different class sets and test photos; not directly comparable)")
fig.tight_layout(); fig.savefig(G / "compare_test_accuracy_baseline_vs_v3.png", dpi=130); plt.close(fig)

# 6. per-class: baseline vs v3 on shared original classes, Split B and A
for s in "AB":
    shared = [c for c in ev[s]["class_names"] if c in bpc[s]]
    x = np.arange(len(shared)); w = 0.4
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.bar(x - w / 2, [bpc[s][c][0] / bpc[s][c][1] for c in shared], w, label="baseline", color="tab:gray")
    ax.bar(x + w / 2, [ev[s]["per_class"][c]["accuracy"] for c in shared], w, label="v3", color="tab:blue")
    ax.set_xticks(x); ax.set_xticklabels(shared, rotation=90, fontsize=8); ax.set_ylim(0, 1.1)
    ax.set_title(f"Split {s}: per-class test accuracy on the 19 shared original students"); ax.legend()
    fig.tight_layout(); fig.savefig(G / f"compare_per_class_baseline_vs_v3_split{s}.png", dpi=130); plt.close(fig)

# 7. v1 failed vs v3: best val acc and final train acc
fig, ax = plt.subplots(figsize=(8, 4.5))
names, vals = [], []
for s in "AB":
    names += [f"v1 failed {s}", f"baseline {s}", f"v3 {s}"]
    vals += [max(v1h[s]["val_acc"]), max(bh[s]["val_acc"]), max(hist[s]["val_acc"])]
ax.bar(range(len(vals)), vals, color=["tab:red", "tab:gray", "tab:green"] * 2)
for i, v in enumerate(vals):
    ax.text(i, v + 0.01, f"{v*100:.1f}%", ha="center", fontsize=9)
ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=30, fontsize=8); ax.set_ylim(0, 1.1)
ax.set_title("Best validation accuracy per run (val sets differ in size; v3 val saturated)")
fig.tight_layout(); fig.savefig(G / "compare_best_val_acc_v1_baseline_v3.png", dpi=130); plt.close(fig)
print(sorted(p.name for p in G.glob("*.png")))
print({s: {"baseline_test": btest[s], "v1_best_val": max(v1h[s]["val_acc"])} for s in "AB"})
