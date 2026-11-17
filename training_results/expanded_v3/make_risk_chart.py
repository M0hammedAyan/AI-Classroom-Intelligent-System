"""Risk-model comparison chart using exactly the report Table 7.5 values (also the values in
evaluation/results/risk_model_evaluation.json). Majority baseline = 107/200 (Section 7.6.2 text)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "graphs_report"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
                     "axes.labelsize": 8, "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.facecolor": "white", "savefig.transparent": False})
models = ["XGBoost", "Logistic Regression"]
acc = [0.5000, 0.3650]
f1 = [0.3286, 0.3183]
base = 107 / 200

with open(OUT / "risk_model_comparison.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["model", "accuracy", "macro_f1", "majority_baseline_accuracy", "test_records"])
    for m, a, b in zip(models, acc, f1):
        w.writerow([m, f"{a:.4f}", f"{b:.4f}", f"{base:.4f}", 200])

x = np.arange(2); wd = 0.34
fig, ax = plt.subplots(figsize=(6.3, 3.6))
b1 = ax.bar(x - wd / 2, acc, wd, color="#4C72B0", edgecolor="black", linewidth=0.6, label="Accuracy")
b2 = ax.bar(x + wd / 2, f1, wd, color="#DD8452", edgecolor="black", linewidth=0.6, hatch="//", label="Macro F1-score")
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.012, f"{r.get_height():.4f}", ha="center", va="bottom", fontsize=8,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0), zorder=5)
ax.axhline(base, color="black", ls="--", lw=1.1, label=f"Majority-class accuracy baseline ({base:.3f})")
ax.set_xticks(x); ax.set_xticklabels(models)
ax.set_ylim(0, 1.0); ax.set_ylabel("Score (0 to 1)")
ax.grid(axis="y", alpha=0.3); ax.set_axisbelow(True)
ax.set_title("Academic Risk Model Comparison on the Held-Out Test Set (n = 200)")
ax.legend(loc="upper right", frameon=False, fontsize=7)
fig.tight_layout()
fig.savefig(OUT / "risk_model_comparison.png", dpi=300)
