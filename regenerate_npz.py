"""
VISTA — Regenerate facial_pipeline_results.npz
================================================
Loads the 711 original images from dataset/, runs SCRFD face detection,
resizes every detected face to 160x160, applies 30 in-memory augmentation
variants per face using Albumentations, extracts a 512-dim ArcFace R50
embedding for every variant, and saves everything to:

    data/processed/facial_pipeline_results.npz

Arrays saved:
    images      (N, 160, 160, 3)  uint8   — augmented face crops (RGB)
    embeddings  (N, 512)          float32 — L2-normalised ArcFace embeddings
    labels      (N,)              object  — student USN string per sample
    metadata    (N,)              object  — dict per sample:
                                    source_image      original filename
                                    student_id        USN
                                    augmentation_index  0-29 (0 = original)
                                    original_bbox     [x1,y1,x2,y2]
                                    det_score         SCRFD confidence

NO new image files are written — everything stays in-memory until the
single .npz save at the end.

Usage:
    python regenerate_npz.py
"""

from __future__ import annotations

import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

# ── Force UTF-8 on Windows CP1252 consoles ──────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
_ROOT       = Path(__file__).resolve().parent
DATASET_DIR = _ROOT / "dataset"
OUTPUT_DIR  = _ROOT / "data" / "processed"
OUTPUT_PATH = OUTPUT_DIR / "facial_pipeline_results.npz"

# ── Constants (must match original pipeline) ─────────────────────────────────
TARGET_SIZE          = (160, 160)   # (width, height) — OpenCV convention
EMBEDDING_DIM        = 512
AUGMENTATIONS_PER_FACE = 30
ONNX_THREADS         = 8
IMG_EXTENSIONS       = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

# Student USNs — discovered dynamically from dataset/ at runtime.
# Populated in run() after verifying the directory exists.
KNOWN_USNS: list[str] = []

# ── Stage 1: InsightFace app ──────────────────────────────────────────────────
def init_insightface():
    from insightface.app import FaceAnalysis
    cv2.setNumThreads(ONNX_THREADS)
    app = FaceAnalysis(
        name="buffalo_l",
        providers=[("CPUExecutionProvider", {"intra_op_num_threads": ONNX_THREADS})],
    )
    app.prepare(ctx_id=-1, det_size=(640, 640))
    logger.info("InsightFace (SCRFD + ArcFace R50) initialised.")
    return app


def detect_and_crop(app, image_path: Path):
    """
    Detect primary face in image_path and return (crop_rgb, face_info).
    Returns (None, None) if no face detected.
    """
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        logger.warning(f"  Cannot read: {image_path.name}")
        return None, None

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    faces   = app.get(img_bgr)
    if not faces:
        logger.warning(f"  No face: {image_path.name}")
        return None, None

    best    = max(faces, key=lambda f: f.det_score)
    x1, y1, x2, y2 = best.bbox.astype(int)
    h, w = img_rgb.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w,  x2), min(h,  y2)
    if x2 <= x1 or y2 <= y1:
        return None, None

    crop = img_rgb[y1:y2, x1:x2].copy()

    # Resize to 160x160 — INTER_AREA down, INTER_CUBIC up
    ch, cw = crop.shape[:2]
    interp = cv2.INTER_AREA if (ch > TARGET_SIZE[1] or cw > TARGET_SIZE[0]) else cv2.INTER_CUBIC
    crop = cv2.resize(crop, TARGET_SIZE, interpolation=interp)

    info = {
        "bbox":      [int(x1), int(y1), int(x2), int(y2)],
        "det_score": float(best.det_score),
    }
    return crop, info


# ── Stage 3: Augmentation pipeline ───────────────────────────────────────────
def build_aug_pipeline():
    import albumentations as A
    pipeline = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.7),
        A.Rotate(limit=15, p=0.5, border_mode=cv2.BORDER_REFLECT_101),
        A.GaussNoise(std_range=(0.04, 0.2), p=0.3),
    ])
    logger.info("Albumentations augmentation pipeline built.")
    return pipeline


def augment(face: np.ndarray, pipeline, n: int = AUGMENTATIONS_PER_FACE) -> list[np.ndarray]:
    """Return n augmented variants of a 160x160 RGB face crop (in-memory only)."""
    return [pipeline(image=face)["image"] for _ in range(n)]


# ── Stage 4: Embedding extraction ────────────────────────────────────────────
def extract_embeddings(app, faces_rgb: list[np.ndarray]) -> np.ndarray:
    """
    Extract ArcFace embeddings for a batch of RGB face crops.
    Uses rec.get_feat() directly (skips re-running SCRFD on tight crops).
    Returns shape (N, 512) float32, L2-normalised.
    """
    if not faces_rgb:
        return np.empty((0, EMBEDDING_DIM), dtype=np.float32)

    rec       = app.models["recognition"]
    faces_bgr = [cv2.cvtColor(f, cv2.COLOR_RGB2BGR) for f in faces_rgb]

    try:
        embs = np.asarray(rec.get_feat(faces_bgr), dtype=np.float32).reshape(-1, EMBEDDING_DIM)
    except Exception as exc:
        logger.warning(f"  Batch embedding failed ({exc}), falling back per-face")
        embs = []
        for fb in faces_bgr:
            try:
                e = np.asarray(rec.get_feat(fb)).reshape(-1).astype(np.float32)
            except Exception:
                e = np.zeros(EMBEDDING_DIM, dtype=np.float32)
            embs.append(e)
        embs = np.stack(embs, axis=0)

    # L2-normalise
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms[norms < 1e-10] = 1.0
    return embs / norms


# ── Main pipeline ─────────────────────────────────────────────────────────────
def run() -> None:
    t_start = time.time()

    logger.info("=" * 65)
    logger.info("  VISTA — Regenerate facial_pipeline_results.npz")
    logger.info(f"  Dataset : {DATASET_DIR}")
    logger.info(f"  Output  : {OUTPUT_PATH}")
    logger.info(f"  Mode    : in-memory augmentation (no image files written)")
    logger.info(f"  Aug/face: {AUGMENTATIONS_PER_FACE}")
    logger.info("=" * 65)

    # ── Discover student folders dynamically ─────────────────────────────────
    global KNOWN_USNS
    KNOWN_USNS = sorted([
        d.name for d in DATASET_DIR.iterdir()
        if d.is_dir()
    ])
    if not KNOWN_USNS:
        raise RuntimeError(f"No student folders found in {DATASET_DIR}")
    logger.info(f"Students found in dataset/: {len(KNOWN_USNS)}")
    for usn in KNOWN_USNS:
        logger.info(f"  {usn}")

    # Initialise models
    app          = init_insightface()
    aug_pipeline = build_aug_pipeline()

    # Accumulators
    all_images:     list[np.ndarray] = []
    all_embeddings: list[np.ndarray] = []
    all_labels:     list[str]        = []
    all_metadata:   list[dict]       = []

    student_stats: dict[str, dict] = {}

    total_students     = len(KNOWN_USNS)
    total_ok           = 0
    total_no_face      = 0
    total_aug          = 0

    for s_idx, usn in enumerate(KNOWN_USNS, 1):
        student_dir = DATASET_DIR / usn
        imgs = sorted([
            f for f in student_dir.iterdir()
            if f.is_file() and f.suffix.lower() in IMG_EXTENSIONS
        ])

        logger.info(f"\n[{s_idx:02d}/{total_students}] {usn}  ({len(imgs)} original images)")
        s_ok  = 0
        s_noface = 0
        s_aug = 0

        for i_idx, img_path in enumerate(imgs, 1):
            # Stage 1+2: detect + crop
            crop, info = detect_and_crop(app, img_path)
            if crop is None:
                s_noface += 1
                continue

            # Stage 3: augment in-memory — produces AUGMENTATIONS_PER_FACE arrays
            aug_faces = augment(crop, aug_pipeline, AUGMENTATIONS_PER_FACE)

            # Stage 4: extract embeddings for the whole batch at once
            embs = extract_embeddings(app, aug_faces)   # (30, 512)

            for aug_idx, (aug_face, emb) in enumerate(zip(aug_faces, embs)):
                all_images.append(aug_face)
                all_embeddings.append(emb)
                all_labels.append(usn)
                all_metadata.append({
                    "source_image":      img_path.name,
                    "student_id":        usn,
                    "augmentation_index": aug_idx,
                    "original_bbox":     info["bbox"],
                    "det_score":         info["det_score"],
                })

            s_ok  += 1
            s_aug += len(aug_faces)

            if i_idx % 5 == 0 or i_idx == len(imgs):
                elapsed = time.time() - t_start
                logger.info(
                    f"  [{i_idx:02d}/{len(imgs)}] {img_path.name}  "
                    f"det_score={info['det_score']:.3f}  "
                    f"aug_samples={s_aug}  elapsed={elapsed:.0f}s"
                )

        total_ok     += s_ok
        total_no_face += s_noface
        total_aug    += s_aug

        student_stats[usn] = {
            "total_images":   len(imgs),
            "faces_detected": s_ok,
            "failed_no_face": s_noface,
            "samples_added":  s_aug,
        }

        logger.info(
            f"  Done {usn}: {s_ok}/{len(imgs)} faces | "
            f"{s_aug} aug samples | {s_noface} no-face"
        )

    # ── Compile arrays ────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 65)
    logger.info("COMPILING ARRAYS")
    logger.info("=" * 65)

    images_arr     = np.stack(all_images,     axis=0).astype(np.uint8)
    embeddings_arr = np.stack(all_embeddings, axis=0).astype(np.float32)
    labels_arr     = np.array(all_labels,     dtype=object)
    metadata_arr   = np.array(all_metadata,   dtype=object)

    logger.info(f"images     : {images_arr.shape}  dtype={images_arr.dtype}")
    logger.info(f"embeddings : {embeddings_arr.shape}  dtype={embeddings_arr.dtype}")
    logger.info(f"labels     : {labels_arr.shape}  dtype={labels_arr.dtype}")
    logger.info(f"metadata   : {metadata_arr.shape}  dtype={metadata_arr.dtype}")

    # ── Save .npz ─────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"\nSaving to {OUTPUT_PATH} ...")
    np.savez_compressed(
        OUTPUT_PATH,
        images=images_arr,
        embeddings=embeddings_arr,
        labels=labels_arr,
        metadata=metadata_arr,
    )
    size_mb = OUTPUT_PATH.stat().st_size / 1024 / 1024
    logger.info(f"Saved  — {size_mb:.1f} MB")

    # ── Final report ──────────────────────────────────────────────────────────
    elapsed = time.time() - t_start
    logger.info("\n" + "=" * 65)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"  Total students      : {total_students}")
    logger.info(f"  Images processed    : {total_ok}  (failed: {total_no_face})")
    logger.info(f"  Total samples in npz: {images_arr.shape[0]}")
    logger.info(f"  Wall time           : {elapsed/60:.1f} min")
    logger.info("=" * 65)

    logger.info("\nPer-student summary:")
    logger.info(f"  {'USN':<18} {'Imgs':>5} {'Faces':>6} {'No-face':>8} {'Samples':>8}")
    logger.info(f"  {'-'*18} {'-'*5} {'-'*6} {'-'*8} {'-'*8}")
    for usn in KNOWN_USNS:
        s = student_stats.get(usn, {})
        logger.info(
            f"  {usn:<18} {s.get('total_images',0):>5} "
            f"{s.get('faces_detected',0):>6} "
            f"{s.get('failed_no_face',0):>8} "
            f"{s.get('samples_added',0):>8}"
        )


if __name__ == "__main__":
    run()
