"""
VISTA — Face Recognition Training Pipeline (ResNet-50 backbone, ArcFace-aligned)
==================================================================================
Trains a ResNet-50 classifier on 21-student classroom face data.

MODEL CLARIFICATION (important for mentors / reports):
    This script uses a torchvision ResNet-50 pretrained on ImageNet, NOT the
    InsightFace buffalo_l ONNX weights.  The reason: InsightFace ships its ArcFace
    R50 as an ONNX model (w600k_r50.onnx), which is read-only inference-only and
    cannot be fine-tuned in PyTorch without exporting and re-importing the weights.
    The ResNet-50 here is the architecturally equivalent backbone, initialised from
    ImageNet rather than MS-Celeb-1M.  ArcFace preprocessing standards (112×112,
    mean=0.5/std=0.5) are preserved.  This is a legitimate training pipeline and
    the correct approach for demonstrating fine-tuning; just do not describe it as
    "ArcFace fine-tuning" in reports — call it "ResNet-50 fine-tune with ArcFace
    preprocessing, trained from ImageNet init".

Usage:
    # Run both splits sequentially
    python train.py

    # Run a specific split
    python train.py --split A
    python train.py --split B

Data layout:
    Original images  : dataset/{USN}/*.jpg            (~30 images per student, direct files)
    Augmented images : agumented data/{USN}/{img_name}/aug_000.jpg ... aug_029.jpg

Split strategy:
    Split A — 80 % train / 10 % val / 10 % test  (on originals, then aug added to train)
    Split B — 70 % train / 15 % val / 15 % test  (same logic)

All outputs are written to training_results/ next to this script.
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

# Force UTF-8 on Windows consoles (avoids CP1252 UnicodeEncodeError for any
# remaining Unicode chars in log output).
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass  # Python < 3.7 fallback — won't occur here

import cv2
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — no display required
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR    = _PROJECT_ROOT / "dataset"
AUG_DIR        = _PROJECT_ROOT / "agumented data"
RESULTS_DIR    = Path(__file__).resolve().parent   # training_results/

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NUM_CLASSES     = 21
IMG_SIZE        = 112          # ArcFace R50 was trained at 112×112
EMBEDDING_DIM   = 512
BATCH_SIZE      = 32
EPOCHS          = 30
EARLY_STOP_PAT  = 7            # patience
LR              = 1e-4
SEED            = 42

# Maximum augmented images to sample per student when added to train.
# Full set = ~1000/student → ~21K total → ~15 min/epoch on CPU (impractical).
# 150/student → ~3.7K train total → ~2 min/epoch on CPU (feasible).
# Set to None to use all augmented images (recommended if CUDA GPU available).
MAX_AUG_PER_STUDENT: int | None = 150

IMG_EXTENSIONS  = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

# The 21 confirmed student USNs (alphabetically sorted — determines class index 0-20)
KNOWN_USNS = [
    "1DA22AI010", "1DA22AI402",
    "1DA23AI001", "1DA23AI004", "1DA23AI005", "1DA23AI009",
    "1DA23AI011", "1DA23AI024", "1DA23AI025", "1DA23AI031",
    "1DA23AI033", "1DA23AI036", "1DA23AI042", "1DA23AI044",
    "1DA23AI047", "1DA23AI049", "1DA23AI050", "1DA23AI055",
    "1DA23AI059",
    "1DA24AI403", "1DA24AI404",
]

SPLIT_CONFIGS = {
    "A": {"train": 0.80, "val": 0.10, "test": 0.10, "tag": "splitA"},
    "B": {"train": 0.70, "val": 0.15, "test": 0.15, "tag": "splitB"},
}

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
def _seed_everything(seed: int = SEED) -> None:
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ===========================================================================
# STAGE 1 — Data Discovery
# ===========================================================================

def discover_original_images(dataset_dir: Path) -> dict[str, list[Path]]:
    """
    Walk dataset_dir and collect original image paths per student USN.

    Structure: dataset/{USN}/*.jpg   (images are direct files, not in sub-dirs)

    Returns:
        { usn: [Path, ...] }  — only USNs present in KNOWN_USNS
    """
    data: dict[str, list[Path]] = {}
    for usn in KNOWN_USNS:
        student_dir = dataset_dir / usn
        if not student_dir.is_dir():
            logger.warning(f"[discover] Missing original folder for {usn}: {student_dir}")
            data[usn] = []
            continue
        imgs = sorted([
            f for f in student_dir.iterdir()
            if f.is_file() and f.suffix.lower() in IMG_EXTENSIONS
        ])
        data[usn] = imgs

    total = sum(len(v) for v in data.values())
    logger.info(f"[discover] Found {total} original images across {len(data)} students.")
    return data


def discover_augmented_images(aug_dir: Path) -> dict[str, list[Path]]:
    """
    Walk augmented data directory and collect all augmented image paths per USN.

    Structure: agumented data/{USN}/{original_img_name}/aug_000.jpg ... aug_029.jpg

    Returns:
        { usn: [Path, ...] }
    """
    data: dict[str, list[Path]] = {}
    for usn in KNOWN_USNS:
        student_dir = aug_dir / usn
        if not student_dir.is_dir():
            logger.warning(f"[discover] Missing augmented folder for {usn}: {student_dir}")
            data[usn] = []
            continue
        imgs = sorted([
            f for sub in sorted(student_dir.iterdir())
            if sub.is_dir()
            for f in sorted(sub.iterdir())
            if f.is_file() and f.suffix.lower() in IMG_EXTENSIONS
        ])
        data[usn] = imgs

    total = sum(len(v) for v in data.values())
    logger.info(f"[discover] Found {total} augmented images across {len(data)} students.")
    return data


# ===========================================================================
# STAGE 2 — Data Splitting  (originals only → then augmented added to train)
# ===========================================================================

def split_originals(
    original_data: dict[str, list[Path]],
    train_ratio: float,
    val_ratio: float,
    seed: int = SEED,
) -> tuple[list[tuple[Path, int]], list[tuple[Path, int]], list[tuple[Path, int]]]:
    """
    Stratified split of original images into train / val / test.

    test_ratio is inferred as 1 - train_ratio - val_ratio.

    Returns:
        train_items, val_items, test_items  — each is a list of (path, class_idx) tuples
        (class_idx is the position in KNOWN_USNS list, 0-indexed)
    """
    train_items: list[tuple[Path, int]] = []
    val_items  : list[tuple[Path, int]] = []
    test_items : list[tuple[Path, int]] = []

    test_ratio = round(1.0 - train_ratio - val_ratio, 6)

    for cls_idx, usn in enumerate(KNOWN_USNS):
        imgs = original_data.get(usn, [])
        if not imgs:
            logger.warning(f"[split] {usn} has NO images — skipped.")
            continue

        n = len(imgs)
        # First cut: carve off test
        if test_ratio > 0 and n >= 3:
            train_val, test = train_test_split(
                imgs,
                test_size=test_ratio,
                random_state=seed,
            )
        else:
            train_val, test = imgs, []

        # Second cut: carve off val from train_val
        if val_ratio > 0 and len(train_val) >= 2:
            val_fraction = val_ratio / (train_ratio + val_ratio)
            train, val = train_test_split(
                train_val,
                test_size=val_fraction,
                random_state=seed,
            )
        else:
            train, val = train_val, []

        train_items.extend([(p, cls_idx) for p in train])
        val_items  .extend([(p, cls_idx) for p in val])
        test_items .extend([(p, cls_idx) for p in test])

    return train_items, val_items, test_items


def add_augmented_to_train(
    train_items: list[tuple[Path, int]],
    aug_data: dict[str, list[Path]],
    train_original_paths: set[Path],
    max_per_student: int | None = MAX_AUG_PER_STUDENT,
) -> list[tuple[Path, int]]:
    """
    Append augmented images for ONLY the students in the train split.

    max_per_student caps how many augmented images are used per student.
    On CPU this is critical: the full ~1000/student set makes each epoch
    ~15 min; 150/student keeps it ~2 min while still providing 5x data
    augmentation over the ~30 originals in train.
    Set max_per_student=None to use every augmented image (needs GPU).
    """
    import random as _random
    rng = _random.Random(SEED)

    train_class_indices = {cls_idx for _, cls_idx in train_items}
    aug_items: list[tuple[Path, int]] = []

    for cls_idx, usn in enumerate(KNOWN_USNS):
        if cls_idx not in train_class_indices:
            continue
        candidates = aug_data.get(usn, [])
        if max_per_student is not None and len(candidates) > max_per_student:
            candidates = rng.sample(candidates, max_per_student)
        for aug_path in candidates:
            aug_items.append((aug_path, cls_idx))

    train_final = train_items + aug_items
    cap_note = f" (capped at {max_per_student}/student)" if max_per_student else " (all aug)"
    logger.info(
        f"[augment] Added {len(aug_items)} augmented images{cap_note} to train "
        f"({len(train_items)} orig -> {len(train_final)} total)."
    )
    return train_final


# ===========================================================================
# STAGE 3 — Dataset & DataLoader
# ===========================================================================

class FaceDataset(Dataset):
    """Loads face images from (path, class_idx) pairs."""

    def __init__(
        self,
        items: list[tuple[Path, int]],
        transform: transforms.Compose,
        is_augmented_set: bool = False,
    ):
        self.items = items
        self.transform = transform
        self.is_augmented_set = is_augmented_set

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        path, label = self.items[idx]
        img_bgr = cv2.imread(str(path))
        if img_bgr is None:
            # Return a black tensor rather than crashing the DataLoader
            img_tensor = torch.zeros(3, IMG_SIZE, IMG_SIZE, dtype=torch.float32)
            return img_tensor, label

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        # Resize to 112×112 (ArcFace native resolution)
        img_rgb = cv2.resize(img_rgb, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_LINEAR)

        from PIL import Image
        img_pil = Image.fromarray(img_rgb)
        img_tensor = self.transform(img_pil)
        return img_tensor, label


def build_transforms(is_train: bool) -> transforms.Compose:
    """
    Build torchvision transform pipeline.

    Train: mild random augmentation on top of ArcFace-standard normalisation.
    Val/Test: deterministic resize + normalise only.
    """
    mean = [0.5, 0.5, 0.5]   # ArcFace standard normalisation
    std  = [0.5, 0.5, 0.5]

    if is_train:
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
            transforms.RandomRotation(degrees=10),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])
    else:
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])


def make_dataloaders(
    train_items: list[tuple[Path, int]],
    val_items  : list[tuple[Path, int]],
    test_items : list[tuple[Path, int]],
    batch_size : int = BATCH_SIZE,
    num_workers: int = 0,
) -> tuple[DataLoader, DataLoader, DataLoader]:
    train_ds = FaceDataset(train_items, build_transforms(is_train=True))
    val_ds   = FaceDataset(val_items,   build_transforms(is_train=False))
    test_ds  = FaceDataset(test_items,  build_transforms(is_train=False))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=num_workers, pin_memory=False)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False,
                              num_workers=num_workers, pin_memory=False)
    test_loader  = DataLoader(test_ds,  batch_size=batch_size, shuffle=False,
                              num_workers=num_workers, pin_memory=False)
    return train_loader, val_loader, test_loader


# ===========================================================================
# STAGE 4 — Model
# ===========================================================================
# ── IMPORTANT NOTE FOR REPORTS / MENTORS ────────────────────────────────────
# The model below is a torchvision ResNet-50 pretrained on ImageNet-1K, NOT a
# direct fine-tune of InsightFace's ArcFace ONNX weights.
#
# Why: InsightFace's buffalo_l pack ships ArcFace R50 as w600k_r50.onnx — a
# frozen inference-only ONNX graph.  Converting an ONNX graph back to trainable
# PyTorch tensors requires exporting all weight tensors and reconstructing the
# iResNet-50 architecture by hand, which is out of scope here.
#
# What this IS: ResNet-50 (same architecture as ArcFace R50) fine-tuned with
# ArcFace-standard preprocessing (112×112 input, mean=0.5 std=0.5 per channel).
# The backbone weight init is ImageNet rather than MS-Celeb-1M.
#
# Correct description for reports: "ResNet-50 fine-tuned on classroom faces,
# using ArcFace input preprocessing, initialised from ImageNet weights."
# ────────────────────────────────────────────────────────────────────────────

class ResNet50FaceClassifier(nn.Module):
    """
    ResNet-50 face classifier for 21-student identification.

    Backbone : torchvision ResNet-50, ImageNet pretrained
    Frozen   : conv1, bn1, layer1, layer2  (low-level feature extractors)
    Trainable: layer3, layer4 (last 2 residual blocks) + classification head
    Head     : 2048 → BN → ReLU → Dropout(0.4) → 512 → BN → ReLU → Dropout(0.3) → 21

    Input    : 112×112 RGB, normalised with mean=0.5 std=0.5 (ArcFace standard)
    """

    def __init__(self, num_classes: int = NUM_CLASSES):
        super().__init__()
        from torchvision.models import resnet50, ResNet50_Weights
        backbone = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)

        # ------------------------------------------------------------------
        # Freeze all layers first
        # ------------------------------------------------------------------
        for param in backbone.parameters():
            param.requires_grad = False

        # ------------------------------------------------------------------
        # Unfreeze last 2 residual blocks (layer3, layer4) + bn1 of each
        # ------------------------------------------------------------------
        for param in backbone.layer3.parameters():
            param.requires_grad = True
        for param in backbone.layer4.parameters():
            param.requires_grad = True
        # Also unfreeze the final BN of the backbone
        for param in backbone.bn1.parameters():
            param.requires_grad = True

        # ------------------------------------------------------------------
        # Strip the original FC and avgpool, keep feature extractor
        # ------------------------------------------------------------------
        self.features = nn.Sequential(
            backbone.conv1,
            backbone.bn1,
            backbone.relu,
            backbone.maxpool,
            backbone.layer1,
            backbone.layer2,
            backbone.layer3,
            backbone.layer4,
            backbone.avgpool,         # global average pool → (B, 2048, 1, 1)
        )

        # ------------------------------------------------------------------
        # Classification head (unfrozen)
        # ------------------------------------------------------------------
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.BatchNorm1d(2048),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.4),
            nn.Linear(2048, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(512, num_classes),
        )

        # Ensure head is trainable
        for param in self.head.parameters():
            param.requires_grad = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.features(x)
        return self.head(feat)

    def trainable_params(self) -> list[nn.Parameter]:
        return [p for p in self.parameters() if p.requires_grad]

    def frozen_param_count(self) -> int:
        return sum(p.numel() for p in self.parameters() if not p.requires_grad)

    def trainable_param_count(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ===========================================================================
# STAGE 5 — Training Loop
# ===========================================================================

def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
) -> tuple[float, float]:
    """Returns (avg_loss, accuracy) for the epoch."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for imgs, labels in loader:
        imgs   = imgs.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad()
        logits = model(imgs)
        loss   = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * imgs.size(0)
        preds   = logits.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total   += imgs.size(0)

    avg_loss = total_loss / max(total, 1)
    accuracy = correct   / max(total, 1)
    return avg_loss, accuracy


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float, list[int], list[int]]:
    """Returns (avg_loss, accuracy, all_labels, all_preds)."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total   = 0
    all_labels: list[int] = []
    all_preds : list[int] = []

    for imgs, labels in loader:
        imgs   = imgs.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        logits = model(imgs)
        loss   = criterion(logits, labels)

        total_loss += loss.item() * imgs.size(0)
        preds   = logits.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total   += imgs.size(0)
        all_labels.extend(labels.cpu().tolist())
        all_preds .extend(preds.cpu().tolist())

    avg_loss = total_loss / max(total, 1)
    accuracy = correct   / max(total, 1)
    return avg_loss, accuracy, all_labels, all_preds


def train_split(
    split_key: str,
    original_data: dict[str, list[Path]],
    aug_data     : dict[str, list[Path]],
    device       : torch.device,
    max_aug      : int | None = MAX_AUG_PER_STUDENT,
) -> None:
    """
    Full training run for one split (A or B).

    Writes to RESULTS_DIR:
        best_model_{tag}.pth
        results_{tag}.txt
        confusion_matrix_{tag}.png
        training_curve_{tag}.png
        data_split_log.txt  (appended with this split's info)
    """
    cfg = SPLIT_CONFIGS[split_key]
    tag = cfg["tag"]
    logger.info("\n" + "=" * 70)
    logger.info(f"  STARTING SPLIT {split_key}  ({int(cfg['train']*100)}/{int(cfg['val']*100)}/{int(cfg['test']*100)})")
    logger.info("=" * 70)

    _seed_everything(SEED)

    # ------------------------------------------------------------------
    # 2a. Split originals
    # ------------------------------------------------------------------
    train_orig, val_items, test_items = split_originals(
        original_data,
        train_ratio=cfg["train"],
        val_ratio=cfg["val"],
        seed=SEED,
    )

    train_orig_paths = {p for p, _ in train_orig}

    # ------------------------------------------------------------------
    # SAFETY ASSERTIONS (pre-augment)
    # ------------------------------------------------------------------
    _assert_no_aug_leakage(val_items,  aug_data, split="val",  tag=tag)
    _assert_no_aug_leakage(test_items, aug_data, split="test", tag=tag)
    _assert_all_classes_in_train({cls for _, cls in train_orig}, tag=tag)

    # ------------------------------------------------------------------
    # 2b. Add augmented to train
    # ------------------------------------------------------------------
    train_items = add_augmented_to_train(train_orig, aug_data, train_orig_paths, max_per_student=max_aug)

    # ------------------------------------------------------------------
    # SAFETY ASSERTIONS (post-augment)
    # ------------------------------------------------------------------
    _assert_no_aug_leakage(val_items,  aug_data, split="val",  tag=tag)
    _assert_no_aug_leakage(test_items, aug_data, split="test", tag=tag)

    # ------------------------------------------------------------------
    # Print class distribution
    # ------------------------------------------------------------------
    _print_class_distribution(train_items, val_items, test_items, tag=tag)

    # ------------------------------------------------------------------
    # Warn if any student has < 3 test images (Split A likely hits this)
    # With 27-41 images per student, Split A gives 2-4 test images each.
    # Split B gives 4-6. Per-class accuracy with < 5 samples is high-variance
    # — individual misses swing from 0% to 100%. This is expected and normal.
    # ------------------------------------------------------------------
    test_cls_counts = defaultdict(int)
    for _, cls in test_items:
        test_cls_counts[cls] += 1
    thin_test_students = []
    for cls_idx, usn in enumerate(KNOWN_USNS):
        cnt = test_cls_counts[cls_idx]
        if cnt < 5:
            thin_test_students.append((usn, cnt))
            logger.warning(
                f"[{tag}] WARNING: {usn} has only {cnt} test image(s) -- "
                f"per-class accuracy for this student is HIGH-VARIANCE "
                f"(one wrong prediction = large % swing)."
            )
    if thin_test_students:
        logger.warning(
            f"[{tag}] {len(thin_test_students)}/{NUM_CLASSES} students have < 5 test images. "
            f"Overall test accuracy is still meaningful; per-class numbers are not. "
            f"This is expected given ~30 images/student and a 10% test split."
        )

    # ------------------------------------------------------------------
    # Write data split log
    # ------------------------------------------------------------------
    _write_data_split_log(train_orig, val_items, test_items, tag=tag)

    # ------------------------------------------------------------------
    # DataLoaders
    # ------------------------------------------------------------------
    train_loader, val_loader, test_loader = make_dataloaders(
        train_items, val_items, test_items,
        batch_size=BATCH_SIZE,
        num_workers=0,      # 0 workers for Windows compatibility
    )
    logger.info(
        f"[{tag}] Loaders ready  — "
        f"train batches={len(train_loader)}  "
        f"val batches={len(val_loader)}  "
        f"test batches={len(test_loader)}"
    )

    # ------------------------------------------------------------------
    # Model
    # ------------------------------------------------------------------
    model     = ResNet50FaceClassifier(num_classes=NUM_CLASSES).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.trainable_params(), lr=LR)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5
    )

    logger.info(
        f"[{tag}] Model — "
        f"trainable params: {model.trainable_param_count():,}  |  "
        f"frozen params: {model.frozen_param_count():,}"
    )

    # ------------------------------------------------------------------
    # Training loop with early stopping
    # ------------------------------------------------------------------
    history: dict[str, list[float]] = {
        "train_loss": [], "train_acc": [],
        "val_loss":   [], "val_acc":   [],
    }

    best_val_acc   = -1.0
    best_state     = None
    patience_count = 0
    best_epoch     = 0

    for epoch in range(1, EPOCHS + 1):
        t0 = time.time()

        tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        vl_loss, vl_acc, _, _ = evaluate(model, val_loader, criterion, device)

        history["train_loss"].append(tr_loss)
        history["train_acc"] .append(tr_acc)
        history["val_loss"]  .append(vl_loss)
        history["val_acc"]   .append(vl_acc)

        scheduler.step(vl_acc)

        elapsed = time.time() - t0
        logger.info(
            f"[{tag}] Epoch {epoch:03d}/{EPOCHS}  "
            f"tr_loss={tr_loss:.4f}  tr_acc={tr_acc:.4f}  "
            f"vl_loss={vl_loss:.4f}  vl_acc={vl_acc:.4f}  "
            f"({elapsed:.1f}s)"
        )

        if vl_acc > best_val_acc:
            best_val_acc   = vl_acc
            best_state     = copy.deepcopy(model.state_dict())
            patience_count = 0
            best_epoch     = epoch
            logger.info(f"[{tag}] ** New best val_acc={best_val_acc:.4f} at epoch {epoch}")
        else:
            patience_count += 1
            if patience_count >= EARLY_STOP_PAT:
                logger.info(
                    f"[{tag}] Early stopping triggered at epoch {epoch} "
                    f"(no improvement for {EARLY_STOP_PAT} epochs). "
                    f"Best was epoch {best_epoch} with val_acc={best_val_acc:.4f}."
                )
                break

    # ------------------------------------------------------------------
    # Save best model
    # ------------------------------------------------------------------
    ckpt_path = RESULTS_DIR / f"best_model_{tag}.pth"
    torch.save({
        "epoch": best_epoch,
        "val_acc": best_val_acc,
        "model_state_dict": best_state,
        "optimizer_state_dict": optimizer.state_dict(),
        "class_names": KNOWN_USNS,
        "split": split_key,
    }, ckpt_path)
    logger.info(f"[{tag}] Saved best model: {ckpt_path}")

    # ------------------------------------------------------------------
    # Evaluation on TEST SET (touched once, here)
    # ------------------------------------------------------------------
    model.load_state_dict(best_state)
    _, test_acc, test_labels, test_preds = evaluate(
        model, test_loader, criterion, device
    )
    logger.info(f"[{tag}] TEST ACCURACY = {test_acc:.4f}")

    # Train vs test gap
    final_train_acc = history["train_acc"][-1]
    gap = abs(final_train_acc - test_acc)
    overfit_warning = ""
    if gap > 0.15:
        overfit_warning = (
            f"\nOVERFITTING WARNING: train/test gap = {gap*100:.1f}%  (> 15%)\n"
            f"   Final train acc = {final_train_acc:.4f}, test acc = {test_acc:.4f}"
        )
        logger.warning(overfit_warning)

    # ------------------------------------------------------------------
    # Per-class accuracy
    # ------------------------------------------------------------------
    per_class_correct = defaultdict(int)
    per_class_total   = defaultdict(int)
    for true, pred in zip(test_labels, test_preds):
        per_class_total[true]   += 1
        if true == pred:
            per_class_correct[true] += 1

    per_class_acc_lines = []
    for cls_idx, usn in enumerate(KNOWN_USNS):
        tot = per_class_total[cls_idx]
        cor = per_class_correct[cls_idx]
        acc = cor / tot if tot > 0 else float("nan")
        per_class_acc_lines.append(f"  {usn} (class {cls_idx:02d}): {cor}/{tot} = {acc:.4f}")

    # ------------------------------------------------------------------
    # Classification report
    # ------------------------------------------------------------------
    clf_report = classification_report(
        test_labels, test_preds,
        target_names=KNOWN_USNS,
        digits=4,
        zero_division=0,
    )

    # ------------------------------------------------------------------
    # Confusion matrix
    # ------------------------------------------------------------------
    cm = confusion_matrix(test_labels, test_preds, labels=list(range(NUM_CLASSES)))
    _save_confusion_matrix(cm, tag=tag)

    # ------------------------------------------------------------------
    # Training curves
    # ------------------------------------------------------------------
    _save_training_curve(history, tag=tag)

    # ------------------------------------------------------------------
    # Write results_*.txt
    # ------------------------------------------------------------------
    _write_results(
        tag=tag,
        split_key=split_key,
        cfg=cfg,
        best_epoch=best_epoch,
        best_val_acc=best_val_acc,
        test_acc=test_acc,
        final_train_acc=final_train_acc,
        gap=gap,
        overfit_warning=overfit_warning,
        per_class_acc_lines=per_class_acc_lines,
        clf_report=clf_report,
        history=history,
        train_size=len(train_items),
        val_size=len(val_items),
        test_size=len(test_items),
        max_aug=max_aug,
    )

    logger.info(f"[{tag}] DONE - Split {split_key} complete. All outputs in {RESULTS_DIR}")


# ===========================================================================
# SAFETY ASSERTIONS & HELPERS
# ===========================================================================

def _assert_no_aug_leakage(
    split_items: list[tuple[Path, int]],
    aug_data: dict[str, list[Path]],
    split: str,
    tag: str,
) -> None:
    """Assert that no augmented image appears in val or test splits."""
    # Build set of all augmented paths (string comparison for efficiency)
    all_aug_paths: set[str] = set()
    for paths in aug_data.values():
        for p in paths:
            all_aug_paths.add(str(p.resolve()))

    leaked = [
        str(p) for p, _ in split_items
        if str(p.resolve()) in all_aug_paths
    ]
    assert not leaked, (
        f"[{tag}] DATA LEAKAGE DETECTED in {split} set! "
        f"{len(leaked)} augmented image(s) found:\n" + "\n".join(leaked[:5])
    )
    logger.info(f"[{tag}] OK - No augmented images in {split} set.")


def _assert_all_classes_in_train(
    train_classes: set[int],
    tag: str,
) -> None:
    """Assert all 21 classes appear in the training set."""
    expected = set(range(NUM_CLASSES))
    missing  = expected - train_classes
    assert not missing, (
        f"[{tag}] MISSING CLASSES in train set: "
        + ", ".join(KNOWN_USNS[i] for i in sorted(missing))
    )
    logger.info(f"[{tag}] OK - All {NUM_CLASSES} classes present in train set.")


def _print_class_distribution(
    train_items: list[tuple[Path, int]],
    val_items  : list[tuple[Path, int]],
    test_items : list[tuple[Path, int]],
    tag: str,
) -> None:
    """Print per-class counts for all three splits."""
    train_counts = defaultdict(int)
    val_counts   = defaultdict(int)
    test_counts  = defaultdict(int)
    for _, c in train_items: train_counts[c] += 1
    for _, c in val_items  : val_counts[c]   += 1
    for _, c in test_items : test_counts[c]   += 1

    lines = [
        f"\n[{tag}] CLASS DISTRIBUTION",
        f"{'USN':<20} {'TRAIN':>8} {'VAL':>6} {'TEST':>6}",
        "-" * 44,
    ]
    for cls_idx, usn in enumerate(KNOWN_USNS):
        lines.append(
            f"{usn:<20} {train_counts[cls_idx]:>8} "
            f"{val_counts[cls_idx]:>6} {test_counts[cls_idx]:>6}"
        )
    lines.append("-" * 44)
    lines.append(
        f"{'TOTAL':<20} {sum(train_counts.values()):>8} "
        f"{sum(val_counts.values()):>6} {sum(test_counts.values()):>6}"
    )
    logger.info("\n".join(lines))


def _write_data_split_log(
    train_orig: list[tuple[Path, int]],
    val_items : list[tuple[Path, int]],
    test_items: list[tuple[Path, int]],
    tag: str,
) -> None:
    """Append this split's image-level assignment to data_split_log.txt."""
    log_path = RESULTS_DIR / "data_split_log.txt"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*70}\n")
        f.write(f"SPLIT {tag.upper()}  —  generated at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*70}\n\n")

        for split_name, items in [("TRAIN (originals only)", train_orig),
                                   ("VAL",   val_items),
                                   ("TEST",  test_items)]:
            f.write(f"--- {split_name} ({len(items)} images) ---\n")
            for path, cls in sorted(items, key=lambda x: (x[1], str(x[0]))):
                f.write(f"  [{KNOWN_USNS[cls]}]  {path}\n")
            f.write("\n")

    logger.info(f"[{tag}] Data split log appended: {log_path}")


def _save_confusion_matrix(cm: np.ndarray, tag: str) -> None:
    """Save confusion matrix as a PNG heatmap."""
    fig, ax = plt.subplots(figsize=(14, 12))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.colorbar(im, ax=ax)

    tick_marks = np.arange(NUM_CLASSES)
    short_names = [usn[-5:] for usn in KNOWN_USNS]   # e.g. AI010
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(short_names, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(short_names, fontsize=8)

    # Annotate cells
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]),
                    ha="center", va="center", fontsize=7,
                    color="white" if cm[i, j] > thresh else "black")

    ax.set_xlabel("Predicted class", fontsize=11)
    ax.set_ylabel("True class",      fontsize=11)
    ax.set_title(f"Confusion Matrix — Split {tag[-1].upper()} (Test Set)", fontsize=13)
    plt.tight_layout()

    out = RESULTS_DIR / f"confusion_matrix_{tag}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[{tag}] Confusion matrix saved: {out}")


def _save_training_curve(history: dict[str, list[float]], tag: str) -> None:
    """Save loss + accuracy training curves as a PNG."""
    epochs = list(range(1, len(history["train_loss"]) + 1))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Loss
    ax1.plot(epochs, history["train_loss"], label="Train Loss", color="tab:blue")
    ax1.plot(epochs, history["val_loss"],   label="Val Loss",   color="tab:orange")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.set_title(f"Loss Curve — Split {tag[-1].upper()}")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Accuracy
    ax2.plot(epochs, [a * 100 for a in history["train_acc"]], label="Train Acc", color="tab:blue")
    ax2.plot(epochs, [a * 100 for a in history["val_acc"]],   label="Val Acc",   color="tab:orange")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy (%)")
    ax2.set_title(f"Accuracy Curve — Split {tag[-1].upper()}")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 105)

    plt.suptitle(f"Training Curves — VISTA ResNet-50 Face Classifier ({tag})", fontsize=13)
    plt.tight_layout()

    out = RESULTS_DIR / f"training_curve_{tag}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[{tag}] Training curve saved: {out}")


def _write_results(
    tag: str,
    split_key: str,
    cfg: dict[str, Any],
    best_epoch: int,
    best_val_acc: float,
    test_acc: float,
    final_train_acc: float,
    gap: float,
    overfit_warning: str,
    per_class_acc_lines: list[str],
    clf_report: str,
    history: dict[str, list[float]],
    train_size: int,
    val_size: int,
    test_size: int,
    max_aug: int | None = MAX_AUG_PER_STUDENT,
) -> None:
    """Write the full evaluation report to results_{tag}.txt."""
    out = RESULTS_DIR / f"results_{tag}.txt"

    lines = [
        "=" * 70,
        f"VISTA — ResNet-50 Face Classifier Results",
        f"(backbone: ImageNet pretrained ResNet-50, ArcFace preprocessing)",
        f"Split {split_key.upper()}  ({int(cfg['train']*100)}/{int(cfg['val']*100)}/{int(cfg['test']*100)})",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
        "DATASET SIZES",
        f"  Train (orig + aug) : {train_size:,} images",
        f"  Val  (orig only)   : {val_size:,}  images",
        f"  Test (orig only)   : {test_size:,}  images",
        f"  Aug cap/student    : {max_aug if max_aug else 'ALL (uncapped)'}",
        "",
        "TRAINING CONFIG",
        f"  Epochs run         : {len(history['train_loss'])}  (max {EPOCHS})",
        f"  Best epoch         : {best_epoch}",
        f"  Early stop patience: {EARLY_STOP_PAT}",
        f"  Batch size         : {BATCH_SIZE}",
        f"  Learning rate      : {LR}",
        f"  Optimizer          : Adam",
        f"  Loss               : CrossEntropyLoss",
        f"  Backbone           : ResNet-50 (ImageNet pretrained, NOT ArcFace ONNX)",
        f"  Input size         : 112x112, mean=0.5 std=0.5 (ArcFace preprocessing)",
        f"  Trainable layers   : layer3 + layer4 + classification head",
        "",
        "ACCURACY SUMMARY",
        f"  Best val accuracy  : {best_val_acc*100:.2f}%",
        f"  Final train acc    : {final_train_acc*100:.2f}%",
        f"  Test accuracy      : {test_acc*100:.2f}%",
        f"  Train / Test gap   : {gap*100:.2f}%",
        "",
        "DATA NOTES",
        f"  Original images per student: 27-41 (varies, actual from dataset/)",
        f"  Test set size per student  : {int(cfg['test']*100)}% of originals = 2-6 images",
        f"  WARNING: Per-class accuracy with < 5 test samples is HIGH-VARIANCE.",
        f"     One wrong prediction can swing a class from 100% to 66%.",
        f"     Overall test accuracy is the reliable metric for this dataset size.",
        f"  Expected overall test accuracy: 70-85% (honest range for this data size)",
        f"  If test accuracy > 95%: re-check data_split_log.txt for leakage.",
    ]
    if overfit_warning:
        lines.append(overfit_warning)

    lines += [
        "",
        "EPOCH LOG (train_loss | train_acc | val_loss | val_acc)",
        "-" * 60,
    ]
    for ep, (tl, ta, vl, va) in enumerate(zip(
        history["train_loss"], history["train_acc"],
        history["val_loss"],   history["val_acc"]
    ), start=1):
        lines.append(f"  Epoch {ep:03d}:  {tl:.4f} | {ta:.4f} | {vl:.4f} | {va:.4f}")

    lines += [
        "",
        "PER-CLASS TEST ACCURACY",
        "-" * 60,
    ]
    lines.extend(per_class_acc_lines)

    lines += [
        "",
        "CLASSIFICATION REPORT (Precision / Recall / F1 per student)",
        "-" * 60,
        clf_report,
        "",
        "=" * 70,
        "END OF REPORT",
        "=" * 70,
    ]

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"[{tag}] Results written: {out}")


# ===========================================================================
# MAIN
# ===========================================================================

def main(splits: list[str] = ("A", "B"), max_aug: int | None = MAX_AUG_PER_STUDENT) -> None:
    logger.info("=" * 70)
    logger.info("  VISTA — Face Recognition Training Pipeline")
    logger.info("  Model: ResNet-50 (ImageNet init, ArcFace preprocessing)")
    logger.info("  NOTE: backbone is ImageNet ResNet-50, NOT ArcFace ONNX weights")
    logger.info(f"  Project root : {_PROJECT_ROOT}")
    logger.info(f"  Results dir  : {RESULTS_DIR}")
    logger.info("=" * 70)

    # Check for PyTorch + GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Device: {device}")
    if device.type == "cpu":
        logger.info(
            "Running on CPU — training will be slow.  "
            "Consider using a CUDA GPU if available."
        )

    # ------------------------------------------------------------------
    # Pre-flight: verify directories exist
    # ------------------------------------------------------------------
    for d, name in [(DATASET_DIR, "dataset"), (AUG_DIR, "agumented data")]:
        if not d.is_dir():
            raise FileNotFoundError(
                f"Required directory not found: {d}\n"
                f"Expected the {name!r} directory at the project root."
            )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Load all data once (shared across both splits)
    # ------------------------------------------------------------------
    logger.info("\n[load] Discovering original images …")
    original_data = discover_original_images(DATASET_DIR)

    logger.info("[load] Discovering augmented images …")
    aug_data = discover_augmented_images(AUG_DIR)

    # Verify both directories have all 21 students
    missing_orig = [usn for usn in KNOWN_USNS if not original_data.get(usn)]
    missing_aug  = [usn for usn in KNOWN_USNS if not aug_data.get(usn)]
    if missing_orig:
        raise RuntimeError(f"Missing original data for students: {missing_orig}")
    if missing_aug:
        logger.warning(f"Missing augmented data for students: {missing_aug}")

    # Summary
    total_orig = sum(len(v) for v in original_data.values())
    total_aug  = sum(len(v) for v in aug_data.values())
    logger.info(f"[load] Total original images : {total_orig}")
    logger.info(f"[load] Total augmented images: {total_aug}")

    # ------------------------------------------------------------------
    # Run each requested split
    # ------------------------------------------------------------------
    for split_key in splits:
        if split_key not in SPLIT_CONFIGS:
            raise ValueError(f"Unknown split key '{split_key}'. Choose from {list(SPLIT_CONFIGS)}")
        train_split(split_key, original_data, aug_data, device, max_aug=max_aug)

    logger.info("\n" + "=" * 70)
    logger.info("  ALL SPLITS COMPLETE")
    logger.info(f"  Outputs in: {RESULTS_DIR}")
    logger.info("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="VISTA — Face recognition training pipeline"
    )
    parser.add_argument(
        "--split",
        choices=["A", "B", "both"],
        default="both",
        help="Which split to run: A (80/10/10), B (70/15/15), or both (default).",
    )
    parser.add_argument(
        "--max-aug",
        type=int,
        default=MAX_AUG_PER_STUDENT,
        metavar="N",
        help=(
            f"Max augmented images per student added to train set "
            f"(default: {MAX_AUG_PER_STUDENT}). "
            f"Use 0 to disable augmentation, -1 to use all (needs GPU)."
        ),
    )
    args = parser.parse_args()
    max_aug_val: int | None = None if args.max_aug < 0 else (args.max_aug or None)

    if args.split == "both":
        main(splits=["A", "B"], max_aug=max_aug_val)
    else:
        main(splits=[args.split], max_aug=max_aug_val)
