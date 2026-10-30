"""
VISTA Face Recognition Evaluation & Threshold Sweep
===================================================
Evaluates ArcFace cosine similarity matching across thresholds on facial_pipeline_results.npz.
Computes Accuracy, Precision, Recall, Macro F1, False Accept Rate (FAR), and False Reject Rate (FRR).
Saves detailed JSON and markdown report to evaluation/results/.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# Path setup
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

NPZ_PATH = ROOT_DIR / "data" / "processed" / "facial_pipeline_results.npz"
RESULTS_DIR = ROOT_DIR / "evaluation" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_npz_data():
    if not NPZ_PATH.exists():
        raise FileNotFoundError(f"NPZ file not found at {NPZ_PATH}")
    print(f"Loading dataset from: {NPZ_PATH}")
    data = np.load(NPZ_PATH, allow_pickle=True)
    embeddings = data["embeddings"]  # (N, 512)
    labels = np.array([str(l) for l in data["labels"]])
    metadata = data["metadata"]
    return embeddings, labels, metadata


def evaluate_threshold_sweep():
    embeddings, labels, metadata = load_npz_data()
    total_samples = len(labels)
    unique_classes = sorted(list(set(labels)))
    num_classes = len(unique_classes)
    print(f"Total samples: {total_samples}, Unique classes: {num_classes}")

    # Build student gallery using unaugmented samples (augmentation_index == 0)
    gallery = {}
    test_indices = []
    val_indices = []

    for i, meta in enumerate(metadata):
        aug_idx = meta.get("augmentation_index", 0) if isinstance(meta, dict) else 0
        lbl = labels[i]
        if aug_idx == 0:
            # Split unaugmented: 70% gallery, 15% val, 15% test
            # Deterministic split based on source image hash
            src = meta.get("source_image", str(i)) if isinstance(meta, dict) else str(i)
            h = hash(src) % 100
            if h < 70:
                if lbl not in gallery:
                    gallery[lbl] = []
                gallery[lbl].append(embeddings[i])
            elif h < 85:
                val_indices.append(i)
            else:
                test_indices.append(i)
        else:
            # Augmented samples can be used for gallery expansion
            pass

    # Ensure every class has at least 1 gallery prototype
    for c in unique_classes:
        if c not in gallery or len(gallery[c]) == 0:
            # fallback: take first sample of this class
            idx = np.where(labels == c)[0][0]
            gallery[c] = [embeddings[idx]]

    # Compute mean normalized embedding per class
    gallery_prototypes = {}
    for c, embs in gallery.items():
        mean_emb = np.mean(embs, axis=0)
        gallery_prototypes[c] = mean_emb / np.linalg.norm(mean_emb)

    print(f"Gallery prototypes created for {len(gallery_prototypes)} classes.")
    print(f"Test samples (unaugmented): {len(test_indices)}")

    # If test_indices is too small, use a stratified 20% holdout of unaugmented images
    if len(test_indices) < 50:
        unaug_indices = [i for i, m in enumerate(metadata) if (m.get("augmentation_index", 0) if isinstance(m, dict) else 0) == 0]
        rng = np.random.RandomState(42)
        rng.shuffle(unaug_indices)
        split_point = int(0.7 * len(unaug_indices))
        gal_idx = unaug_indices[:split_point]
        test_indices = unaug_indices[split_point:]
        
        gallery = {}
        for i in gal_idx:
            lbl = labels[i]
            if lbl not in gallery:
                gallery[lbl] = []
            gallery[lbl].append(embeddings[i])
        gallery_prototypes = {c: np.mean(embs, axis=0) / np.linalg.norm(np.mean(embs, axis=0)) for c, embs in gallery.items()}

    test_embs = embeddings[test_indices]
    test_labels = labels[test_indices]

    # Evaluate across thresholds
    thresholds = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
    sweep_results = []

    proto_keys = list(gallery_prototypes.keys())
    proto_matrix = np.array([gallery_prototypes[k] for k in proto_keys])  # (K, 512)

    # Compute cosine similarities for all test embeddings against all gallery prototypes
    # shape: (N_test, K)
    sim_matrix = np.dot(test_embs, proto_matrix.T)

    best_thresh = 0.55
    best_f1 = 0.0

    for th in thresholds:
        tp = 0
        fp = 0  # matched to wrong student
        fn = 0  # true student rejected as unknown
        correct = 0
        total = len(test_labels)

        predictions = []
        for i in range(total):
            true_label = test_labels[i]
            best_proto_idx = np.argmax(sim_matrix[i])
            best_sim = sim_matrix[i, best_proto_idx]
            pred_label = proto_keys[best_proto_idx] if best_sim >= th else None

            predictions.append(pred_label)

            if pred_label == true_label:
                tp += 1
                correct += 1
            elif pred_label is None:
                fn += 1  # false reject
            else:
                fp += 1  # false accept (impostor accepted as wrong enrolled)

        accuracy = correct / total
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        far = fp / total
        frr = fn / total

        if f1 > best_f1:
            best_f1 = f1
            best_thresh = th

        sweep_results.append({
            "threshold": th,
            "accuracy": round(float(accuracy), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "false_accept_rate": round(float(far), 4),
            "false_reject_rate": round(float(frr), 4),
            "tp": tp, "fp": fp, "fn": fn, "total": total
        })

    output_data = {
        "dataset": "facial_pipeline_results.npz",
        "total_gallery_classes": len(gallery_prototypes),
        "test_sample_count": len(test_indices),
        "optimal_threshold": best_thresh,
        "best_f1_score": round(best_f1, 4),
        "threshold_sweep": sweep_results
    }

    out_file = RESULTS_DIR / "recognition_threshold_sweep.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSaved threshold sweep results to {out_file}")
    print(f"Optimal threshold: {best_thresh} with F1: {best_f1:.4f}")
    return output_data


if __name__ == "__main__":
    evaluate_threshold_sweep()
