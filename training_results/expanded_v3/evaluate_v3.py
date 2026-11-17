"""Evaluate v3 checkpoints (Split A, B) on their clean-photo TEST sets. No tuning on test."""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from train_expanded_v3 import ResNet50FaceClassifier, IMG_SIZE  # noqa: E402

OUT = ROOT / "training_results" / "expanded_v3"
NPZ = ROOT / "data" / "processed" / "facial_pipeline_results_expanded_v3.npz"


def wilson(k, n, z=1.959964):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def acc_block(y, p, mask):
    n = int(mask.sum())
    k = int((y[mask] == p[mask]).sum())
    return {"correct": k, "n": n, "accuracy": k / n if n else None, "wilson95": wilson(k, n)}


def main():
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    d = np.load(NPZ, allow_pickle=True)
    images, meta = d["images"], d["metadata"]
    rows = {}
    for i, m in enumerate(meta):
        m = m.item() if hasattr(m, "item") else m
        if int(m["augmentation_index"]) == 0:
            rows[(m["student_id"], m["source_image"])] = i
    norm = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])
    results = {}
    for split in ("A", "B"):
        sp = json.loads((OUT / f"splits_{split}.json").read_text(encoding="utf-8"))
        classes = sp["classes"]
        ci = {c: i for i, c in enumerate(classes)}
        ck = torch.load(OUT / f"best_model_expanded_v3_split{split}.pth", map_location="cpu", weights_only=False)
        assert ck["class_names"] == classes
        model = ResNet50FaceClassifier(len(classes))
        model.load_state_dict(ck["model_state_dict"])
        model.to(dev).eval()
        idx = [rows[(e["usn"], e["source_image"])] for e in sp["test"]]
        y = np.array([ci[e["usn"]] for e in sp["test"]])
        preds = []
        with torch.no_grad():
            for s in range(0, len(idx), 32):
                x = torch.stack([norm(Image.fromarray(images[i]).resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR))
                                 for i in idx[s:s + 32]]).to(dev)
                preds.extend(model(x).argmax(1).cpu().tolist())
        p = np.array(preds)
        n_cls = len(classes)
        cm = confusion_matrix(y, p, labels=list(range(n_cls)))
        pr, rc, f1, _ = precision_recall_fscore_support(y, p, labels=list(range(n_cls)), average="macro", zero_division=0)
        new_mask_cls = np.array([c.startswith("1DA25AI") for c in classes])
        is_new = new_mask_cls[y]
        per_class = {}
        for i, c in enumerate(classes):
            m = y == i
            per_class[c] = {"correct": int((p[m] == i).sum()), "n": int(m.sum()),
                            "accuracy": float((p[m] == i).mean()) if m.sum() else None}
        # original-19 restricted view of the same model: test samples of original students only
        results[split] = {
            "checkpoint_epoch": ck["epoch"], "checkpoint_val_acc": ck["val_acc"],
            "n_test": int(len(y)), "n_classes": n_cls,
            "overall": acc_block(y, p, np.ones(len(y), bool)),
            "original_19": acc_block(y, p, ~is_new),
            "new_10": acc_block(y, p, is_new),
            "macro_precision": pr, "macro_recall": rc, "macro_f1": f1,
            "class_names": classes, "per_class": per_class,
            "confusion_matrix": cm.tolist(),
            "misclassified": [{"usn": sp["test"][j]["usn"], "source_image": sp["test"][j]["source_image"],
                               "pred": classes[p[j]]} for j in range(len(y)) if p[j] != y[j]],
        }
        # original students only: predictions still over 29 classes (any wrong label counts as error)
        r = results[split]
        print(split, "ckpt epoch", r["checkpoint_epoch"], "val", r["checkpoint_val_acc"], "n", r["n_test"])
        for k in ("overall", "original_19", "new_10"):
            print("  ", k, r[k])
        print("   macro P/R/F1", pr, rc, f1)
    (OUT / "eval_results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
