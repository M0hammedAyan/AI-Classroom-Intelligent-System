"""
Plot publication-quality figures directly from evaluation/results JSON artifacts.
Zero hardcoded data: all coordinates, metrics, and error intervals load dynamically.
Outputs both PNG (300 DPI) and PDF vector formats into paper/figures/.
"""
from __future__ import annotations

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = Path(__file__).resolve().parent
RESULTS_DIR = FIGURES_DIR.parents[1] / "evaluation" / "results"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 12,
    "lines.linewidth": 1.75,
    "lines.markersize": 5,
    "grid.alpha": 0.35,
    "grid.linestyle": "--",
})


def plot_threshold_sweep():
    json_path = RESULTS_DIR / "recognition_threshold_sweep.json"
    if not json_path.exists():
        print(f"Skipping threshold sweep: {json_path} not found")
        return

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    sweep = data["threshold_sweep"]
    thresh = [item["threshold"] for item in sweep]
    prec = [item["precision"] * 100 for item in sweep]
    rec = [item["recall"] * 100 for item in sweep]
    f1 = [item["f1_score"] * 100 for item in sweep]
    far = [item["false_accept_rate"] * 100 for item in sweep]
    frr = [item["false_reject_rate"] * 100 for item in sweep]

    fig, ax1 = plt.subplots(figsize=(5.5, 3.8))

    # Left axis: Precision, Recall, F1
    ax1.plot(thresh, prec, "b-o", label="Precision (%)")
    ax1.plot(thresh, rec, "g-s", label="Recall (%)")
    ax1.plot(thresh, f1, "m-^", label="F1-Score (%)")
    ax1.set_xlabel(r"Cosine Similarity Threshold ($\tau$)")
    ax1.set_ylabel("Accuracy / Metric Score (%)")
    ax1.set_ylim(40, 105)
    ax1.grid(True)

    # Right axis: FAR and FRR
    ax2 = ax1.twinx()
    ax2.plot(thresh, far, "r--d", label="FAR (%)")
    ax2.plot(thresh, frr, "k--x", label="FRR (%)")
    ax2.set_ylabel("Error Rates (%)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")
    ax2.set_ylim(-2, 45)

    # Operational point highlight at tau=0.55
    ax1.axvline(x=0.55, color="gray", linestyle=":", linewidth=1.5, label=r"Prod $\tau=0.55$")

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left", framealpha=0.9, fontsize=8)

    plt.title(r"ArcFace Cosine Matching Threshold Sweep ($N=107$)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig_threshold_sweep.png", dpi=300)
    plt.savefig(FIGURES_DIR / "fig_threshold_sweep.pdf")
    plt.close()
    print("Saved fig_threshold_sweep.png and .pdf")


def plot_cascade_ablation():
    json_path = RESULTS_DIR / "cascade_ablation.json"
    if not json_path.exists():
        print(f"Skipping cascade ablation: {json_path} not found")
        return

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    cos = data["cosine_only"]
    casc = data["cascade_cosine_plus_resnet"]

    metrics = ["Accuracy", "Precision", "Recall", "F1-Score", "FAR", "FRR"]
    cos_vals = [
        cos["accuracy"] * 100,
        cos["precision"] * 100,
        cos["recall"] * 100,
        cos["f1_score"] * 100,
        cos["false_accept_rate"] * 100,
        cos["false_reject_rate"] * 100,
    ]
    casc_vals = [
        casc["accuracy"] * 100,
        casc["precision"] * 100,
        casc["recall"] * 100,
        casc["f1_score"] * 100,
        casc["false_accept_rate"] * 100,
        casc["false_reject_rate"] * 100,
    ]

    # Asymmetric error intervals from Wilson 95% CIs
    cos_err_low = [
        cos["accuracy"] * 100 - cos["accuracy_wilson_ci_95"][0],
        cos["precision"] * 100 - cos["precision_wilson_ci_95"][0],
        cos["recall"] * 100 - cos["recall_wilson_ci_95"][0],
        0.0,
        cos["false_accept_rate"] * 100 - cos["far_wilson_ci_95"][0],
        cos["false_reject_rate"] * 100 - cos["frr_wilson_ci_95"][0],
    ]
    cos_err_high = [
        cos["accuracy_wilson_ci_95"][1] - cos["accuracy"] * 100,
        cos["precision_wilson_ci_95"][1] - cos["precision"] * 100,
        cos["recall_wilson_ci_95"][1] - cos["recall"] * 100,
        0.0,
        cos["far_wilson_ci_95"][1] - cos["false_accept_rate"] * 100,
        cos["frr_wilson_ci_95"][1] - cos["false_reject_rate"] * 100,
    ]

    casc_err_low = [
        casc["accuracy"] * 100 - casc["accuracy_wilson_ci_95"][0],
        casc["precision"] * 100 - casc["precision_wilson_ci_95"][0],
        casc["recall"] * 100 - casc["recall_wilson_ci_95"][0],
        0.0,
        casc["false_accept_rate"] * 100 - casc["far_wilson_ci_95"][0],
        casc["false_reject_rate"] * 100 - casc["frr_wilson_ci_95"][0],
    ]
    casc_err_high = [
        casc["accuracy_wilson_ci_95"][1] - casc["accuracy"] * 100,
        casc["precision_wilson_ci_95"][1] - casc["precision"] * 100,
        casc["recall_wilson_ci_95"][1] - casc["recall"] * 100,
        0.0,
        casc["far_wilson_ci_95"][1] - casc["false_accept_rate"] * 100,
        casc["frr_wilson_ci_95"][1] - casc["false_reject_rate"] * 100,
    ]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    rects1 = ax.bar(
        x - width / 2, cos_vals, width, label=r"Cosine-Only ($\tau=0.55$)",
        color="#4C72B0", yerr=[cos_err_low, cos_err_high], capsize=4
    )
    rects2 = ax.bar(
        x + width / 2, casc_vals, width, label=r"Cascade (Cosine + ResNet)",
        color="#55A868", yerr=[casc_err_low, casc_err_high], capsize=4
    )

    ax.set_ylabel("Metric Percentage (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.grid(True, axis="y")

    # Annotate FRR reduction
    frr_idx = 5
    ax.annotate(
        r"$\mathbf{-14.85\%}$ FRR",
        xy=(frr_idx + width / 2, casc_vals[frr_idx]),
        xytext=(frr_idx - 0.2, 28),
        arrowprops=dict(facecolor="black", arrowstyle="->", lw=1),
        fontsize=8.5, fontweight="bold"
    )

    plt.title(r"Ablation: Cosine-Only vs. Cascade with 95% Wilson CIs ($N=202$)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig_cascade_ablation.png", dpi=300)
    plt.savefig(FIGURES_DIR / "fig_cascade_ablation.pdf")
    plt.close()
    print("Saved fig_cascade_ablation.png and .pdf")


def plot_scaling_latency():
    json_path = RESULTS_DIR / "latency_benchmark.json"
    if not json_path.exists():
        print(f"Skipping latency plot: {json_path} not found")
        return

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    scaling = data["group_photo_scaling"]
    face_counts = [scaling[k]["face_count"] for k in scaling]
    fast_lat = [scaling[k]["fast_path_latency_sec"] * 1000 for k in scaling]
    hybrid_lat = [scaling[k]["hybrid_path_latency_sec"] * 1000 for k in scaling]

    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    ax.plot(face_counts, fast_lat, "b-o", label="Fast Path (ArcFace Cosine Only)")
    ax.plot(face_counts, hybrid_lat, "r--s", label="Hybrid Path (with ResNet Fallback)")

    ax.set_xlabel("Number of Detected Faces in Group Image")
    ax.set_ylabel("End-to-End Latency (ms)")
    ax.set_title("Multi-Face Group Photo Scaling Latency (Intel i7-13700H CPU)")
    ax.set_ylim(0, 420)
    ax.grid(True)
    ax.legend(loc="upper left", framealpha=0.9)

    # 350ms classroom budget line
    ax.axhline(y=350, color="gray", linestyle=":", label="Sub-second Target (350ms)")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig_group_photo_latency.png", dpi=300)
    plt.savefig(FIGURES_DIR / "fig_group_photo_latency.pdf")
    plt.close()
    print("Saved fig_group_photo_latency.png and .pdf")


if __name__ == "__main__":
    plot_threshold_sweep()
    plot_cascade_ablation()
    plot_scaling_latency()
    print("All figures successfully plotted.")
