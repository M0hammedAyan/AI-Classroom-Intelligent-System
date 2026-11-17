"""
VISTA - train ResNet-50 face classifier on the v3 npz (29 classes).

Usage:  python train_expanded_v3.py --split A|B [--smoke] [--epochs N]
Splits come from training_results/expanded_v3/splits_{A,B}.json (by source photo).
Same recipe as train_from_npz.py (112x112 RGB, mean=std=0.5, frozen conv1/layer1/layer2,
same head, Adam, ReduceLROnPlateau) plus label smoothing 0.1 and class-weighted loss.
Preprocessing channel order: npz images are RGB uint8, fed via PIL -> ToTensor with no
channel flip, identical to train_from_npz.py.
"""
from __future__ import annotations

import argparse
import copy
import json
import logging
import random
import sys
import time
import traceback
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.models import ResNet50_Weights, resnet50

ROOT = Path(__file__).resolve().parent
NPZ_PATH = ROOT / "data" / "processed" / "facial_pipeline_results_expanded_v3.npz"
OUT_DIR = ROOT / "training_results" / "expanded_v3"
STATUS_PATH = ROOT / ".agents" / "tasks" / "dataset-expansion" / "train_status_v3.json"

IMG_SIZE = 112
BATCH_SIZE = 32
MAX_EPOCHS = 30
PATIENCE = 7
SEED = 42
LABEL_SMOOTHING = 0.1

logger = logging.getLogger("train_v3")


def write_status(done: str, split: str, epoch: int, error: str = "") -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(
        json.dumps({"done": done, "split": split, "epoch": epoch, "error": error}),
        encoding="utf-8",
    )


def seed_all(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


class NPZFaceDataset(Dataset):
    def __init__(self, images, indices, labels, transform):
        self.images, self.indices, self.labels, self.transform = images, indices, labels, transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, pos):
        i = self.indices[pos]
        img = Image.fromarray(self.images[i]).resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
        return self.transform(img), self.labels[i]


def build_transforms(is_train: bool):
    norm = transforms.Normalize([0.5] * 3, [0.5] * 3)
    if is_train:
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.3),
            transforms.ColorJitter(brightness=0.15, contrast=0.15),
            transforms.ToTensor(), norm,
        ])
    return transforms.Compose([transforms.ToTensor(), norm])


class ResNet50FaceClassifier(nn.Module):
    """Identical architecture to train_from_npz.py; fresh ImageNet weights, new random head."""

    def __init__(self, num_classes: int):
        super().__init__()
        bb = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        for p in bb.parameters():
            p.requires_grad = False
        for layer in (bb.layer3, bb.layer4, bb.bn1):
            for p in layer.parameters():
                p.requires_grad = True
        self.features = nn.Sequential(
            bb.conv1, bb.bn1, bb.relu, bb.maxpool,
            bb.layer1, bb.layer2, bb.layer3, bb.layer4, bb.avgpool,
        )
        self.head = nn.Sequential(
            nn.Flatten(), nn.BatchNorm1d(2048), nn.ReLU(inplace=True), nn.Dropout(0.4),
            nn.Linear(2048, 512), nn.BatchNorm1d(512), nn.ReLU(inplace=True), nn.Dropout(0.3),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        return self.head(self.features(x))


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    tl = correct = total = 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        out = model(imgs)
        loss = criterion(out, labels)
        if not torch.isfinite(loss):
            raise FloatingPointError(f"NaN/inf training loss: {loss.item()}")
        loss.backward()
        optimizer.step()
        tl += loss.item() * imgs.size(0)
        correct += (out.argmax(1) == labels).sum().item()
        total += imgs.size(0)
    return tl / max(total, 1), correct / max(total, 1)


@torch.no_grad()
def eval_epoch(model, loader, criterion, device):
    model.eval()
    tl = correct = total = 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        out = model(imgs)
        loss = criterion(out, labels)
        if not torch.isfinite(loss):
            raise FloatingPointError(f"NaN/inf validation loss: {loss.item()}")
        tl += loss.item() * imgs.size(0)
        correct += (out.argmax(1) == labels).sum().item()
        total += imgs.size(0)
    return tl / max(total, 1), correct / max(total, 1)


def run(args) -> None:
    split = args.split
    out_dir = OUT_DIR / "smoke" if args.smoke else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Device: {device}" + (f" ({torch.cuda.get_device_name(0)})" if device.type == "cuda" else ""))
    if device.type != "cuda":
        raise RuntimeError("CUDA is required but not available")
    seed_all(SEED)

    sp = json.loads((OUT_DIR / f"splits_{split}.json").read_text(encoding="utf-8"))
    class_names = list(sp["classes"])
    num_classes = len(class_names)
    cls_idx = {c: i for i, c in enumerate(class_names)}
    logger.info(f"Split {split}: NUM_CLASSES = {num_classes}")

    logger.info(f"Loading {NPZ_PATH} ...")
    d = np.load(NPZ_PATH, allow_pickle=True)
    images = d["images"]
    labels_raw = d["labels"]
    meta = d["metadata"]
    labels = np.array([cls_idx[str(l)] for l in labels_raw], dtype=np.int64)

    # (usn, source) -> {aug_idx: row}
    rows = defaultdict(dict)
    for i, m in enumerate(meta):
        m = m.item() if hasattr(m, "item") else m
        rows[(m["student_id"], m["source_image"])][int(m["augmentation_index"])] = i

    def collect(entries, clean_only):
        idx = []
        for e in entries:
            g = rows[(e["usn"], e["source_image"])]
            idx.extend([g[0]] if clean_only else sorted(g.values()))
        return idx

    train_idx = collect(sp["train"], False)
    val_idx = collect(sp["val"], True)
    test_idx = collect(sp["test"], True)
    assert not set(train_idx) & set(val_idx) and not set(train_idx) & set(test_idx) \
        and not set(val_idx) & set(test_idx), "index leakage"
    assert len(train_idx) == sp["n_samples"]["train"] and len(val_idx) == sp["n_samples"]["val"] \
        and len(test_idx) == sp["n_samples"]["test"], "split size mismatch vs splits json"
    logger.info(f"Samples: train={len(train_idx)} val={len(val_idx)} test={len(test_idx)} (test untouched here)")

    if args.smoke:
        rng = random.Random(SEED)
        train_idx = rng.sample(train_idx, min(args.smoke_train, len(train_idx)))
        val_idx = val_idx[:: max(1, len(val_idx) // 64)][:64]
        logger.info(f"SMOKE subset: train={len(train_idx)} val={len(val_idx)}")

    # class weights from train counts: inverse frequency, normalised to mean 1
    counts = np.bincount(labels[train_idx], minlength=num_classes).astype(np.float64)
    w = np.where(counts > 0, counts.sum() / (num_classes * np.maximum(counts, 1)), 0.0)
    w = w / w[counts > 0].mean()
    logger.info(f"Class weights min={w[counts>0].min():.3f} max={w.max():.3f}")
    weight_t = torch.tensor(w, dtype=torch.float32, device=device)

    kw = dict(num_workers=0, pin_memory=True)
    tr_loader = DataLoader(NPZFaceDataset(images, train_idx, labels, build_transforms(True)),
                           batch_size=BATCH_SIZE, shuffle=True, **kw)
    va_loader = DataLoader(NPZFaceDataset(images, val_idx, labels, build_transforms(False)),
                           batch_size=BATCH_SIZE, shuffle=False, **kw)

    model = ResNet50FaceClassifier(num_classes).to(device)
    criterion = nn.CrossEntropyLoss(weight=weight_t, label_smoothing=LABEL_SMOOTHING)
    # val loss reported unweighted-by-class-weights for comparability? keep same criterion.
    backbone_params = [p for p in model.features.parameters() if p.requires_grad]
    head_params = list(model.head.parameters())
    optimizer = optim.Adam([
        {"params": backbone_params, "lr": args.backbone_lr},
        {"params": head_params, "lr": args.head_lr},
    ])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=4)
    logger.info(f"LR backbone={args.backbone_lr} head={args.head_lr} label_smoothing={LABEL_SMOOTHING} "
                f"patience={PATIENCE} max_epochs={args.epochs}")

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    best_acc, best_state, best_epoch, bad = -1.0, None, 0, 0
    write_status("no", split, 0)

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        tl, ta = train_epoch(model, tr_loader, criterion, optimizer, device)
        vl, va = eval_epoch(model, va_loader, criterion, device)
        scheduler.step(va)
        for k, v in zip(history, (tl, ta, vl, va)):
            history[k].append(v)
        flag = ""
        if va > best_acc:
            best_acc, best_state, best_epoch, bad = va, copy.deepcopy(model.state_dict()), epoch, 0
            flag = "  ** best"
        else:
            bad += 1
        logger.info(f"[{split}] Epoch {epoch:03d}/{args.epochs} tr_loss={tl:.4f} tr_acc={ta:.4f} "
                    f"vl_loss={vl:.4f} vl_acc={va:.4f} ({time.time()-t0:.0f}s){flag}")
        if not args.smoke:
            write_status("no", split, epoch)
        (out_dir / f"history_split{split}.json").write_text(json.dumps(history, indent=1), encoding="utf-8")
        if bad >= PATIENCE:
            logger.info(f"Early stop at epoch {epoch}; best epoch {best_epoch} val_acc={best_acc:.4f}")
            break

    torch.save({
        "epoch": best_epoch, "val_acc": best_acc, "model_state_dict": best_state,
        "class_names": class_names, "num_classes": num_classes, "split": split,
        "lr": {"backbone": args.backbone_lr, "head": args.head_lr},
    }, out_dir / f"best_model_expanded_v3_split{split}.pth")
    logger.info(f"[{split}] saved checkpoint + history in {out_dir} (best epoch {best_epoch}, val_acc {best_acc:.4f})")
    if args.smoke:
        return
    # A finished -> B still pending; only B finishing sets done=yes
    if split == "B":
        write_status("yes", "B", len(history["train_loss"]))
    else:
        write_status("no", "B", len(history["train_loss"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=["A", "B"])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--smoke-train", type=int, default=1500)
    ap.add_argument("--epochs", type=int, default=None)
    ap.add_argument("--backbone-lr", type=float, default=1e-4)
    ap.add_argument("--head-lr", type=float, default=1e-4)
    args = ap.parse_args()
    if args.epochs is None:
        args.epochs = 1 if args.smoke else MAX_EPOCHS
    args.epochs = min(args.epochs, MAX_EPOCHS)

    handlers = [logging.StreamHandler(sys.stdout)]
    if not args.smoke:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(OUT_DIR / f"train_log_split{args.split}.txt", encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=handlers)

    try:
        run(args)
    except BaseException as e:  # noqa: BLE001
        logger.error("FAILED: %s\n%s", e, traceback.format_exc())
        if not args.smoke:
            write_status("no", args.split, 0, f"{type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
