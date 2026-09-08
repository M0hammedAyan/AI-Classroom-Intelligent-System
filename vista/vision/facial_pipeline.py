"""
End-to-End Facial Pipeline with Structured Nested-Loop Processing
===================================================================
Processes a multi-student dataset through a complete facial recognition pipeline:

    OUTER  — iterate over student subfolders (e.g. 21 students)
    MIDDLE — iterate over raw images per student (~30-40 each)
    INNER  — generate 30 augmented variants per face

Pipeline stages:
1. Face Extraction (InsightFace SCRFD)
2. Data Preprocessing (resize to 160x160)
3. Data Augmentation (30 variants per face using Albumentations)
4. Facial Feature Extraction (ArcFace R50 → 512-dim embeddings)
5. Global Data Compilation (master arrays)

Dependencies:
- opencv-python
- insightface
- albumentations
- numpy
- onnxruntime
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

INPUT_DIR = Path(r"D:\MDA\AI-Classroom-Intelligent-System\dataset")  # Dataset with student subfolders
TARGET_SIZE = (160, 160)                     # Target face crop size
EMBEDDING_DIM = 512                          # ArcFace R50 embedding dimension
AUGMENTATIONS_PER_FACE = 30                  # Number of augmented variants per face

# --- Resource tuning (this machine: 20 logical cores, no CUDA GPU, 8 GB RAM) ---
# Limiting the number of inference threads keeps CPU clocks high and avoids severe
# thermal throttling, which caused progressive slowdowns (9s -> 50s/image).
# An NVIDIA CUDA GPU would be preferred; Intel iGPU (DirectML) measured SLOWER than CPU.
USE_CUDA_GPU = False
ONNX_INTRA_OP_THREADS = 8
CV2_THREADS = 8
# Single worker: 2 workers x ~1.2GB model WS overflows the 2.2GB free RAM and
# causes page-file thrashing (throughput collapsed to 80s/img). One worker holds
# the whole pipeline in memory and sustains ~14s/img without thrash.
NUM_WORKER_PROCESSES = 1

# Face-safe augmentation configuration
AUGMENTATION_CONFIG = {
    "horizontal_flip": {"p": 0.5},
    "brightness_contrast": {"brightness_limit": 0.2, "contrast_limit": 0.2, "p": 0.7},
    "rotate": {"limit": 15, "p": 0.5},
    "gauss_noise": {"std_range": (0.04, 0.2), "p": 0.3},  # normalized: ~10-50 pixel std
}


# =============================================================================
# STAGE 1: FACE EXTRACTION (using InsightFace SCRFD)
# =============================================================================

def build_providers() -> list[Any]:
    """
    Build the onnxruntime provider list for InsightFace sessions.

    Uses CPU with a bounded intra-op thread pool (avoids thermal throttling).
    If USE_CUDA_GPU is enabled and CUDAExecutionProvider is available, it is used.
    """
    cpu_opt = ("CPUExecutionProvider", {
        "intra_op_num_threads": ONNX_INTRA_OP_THREADS,
    })
    if USE_CUDA_GPU:
        return ["CUDAExecutionProvider", cpu_opt]
    return [cpu_opt]


def initialize_face_detector(det_size: tuple[int, int] = (640, 640), providers: list[Any] | None = None) -> Any:
    """
    Initialize and return the InsightFace FaceAnalysis app (lazy-loaded).
    Returns the detector instance with SCRFD + ArcFace R50 models loaded.
    """
    try:
        from insightface.app import FaceAnalysis
    except ImportError as e:
        logger.error("insightface not installed. Run: pip install insightface")
        raise

    if providers is None:
        providers = build_providers()

    cv2.setNumThreads(CV2_THREADS)

    app = FaceAnalysis(
        name="buffalo_l",              # Includes SCRFD detector + ArcFace R50 recognizer
        providers=providers,
    )
    app.prepare(ctx_id=-1, det_size=det_size)
    logger.info("Face detector (SCRFD + ArcFace R50) initialized successfully.")
    return app


def extract_primary_face(app: Any, image_path: str) -> tuple[np.ndarray | None, dict | None]:
    """
    Detect faces in an image and extract the primary (highest confidence) face crop.

    Args:
        app: Initialized InsightFace FaceAnalysis instance
        image_path: Path to input image

    Returns:
        Tuple of (face_crop_rgb, face_info_dict) or (None, None) if no face detected
        face_crop_rgb: Cropped face as RGB numpy array (H, W, 3)
        face_info_dict: Contains bbox, det_score, landmarks
    """
    # Load image
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        logger.warning(f"Failed to load image: {image_path}")
        return None, None

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Detect faces
    faces = app.get(img_bgr)
    if not faces:
        logger.warning(f"No face detected in: {image_path}")
        return None, None

    # Select primary face (highest detection score)
    primary_face = max(faces, key=lambda f: f.det_score)

    # Extract bounding box
    bbox = primary_face.bbox.astype(int)
    x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]

    # Handle edge cases: clamp to image boundaries
    h, w = img_rgb.shape[:2]
    x1 = max(0, min(x1, w - 1))
    y1 = max(0, min(y1, h - 1))
    x2 = max(0, min(x2, w))
    y2 = max(0, min(y2, h))

    # Ensure valid crop region
    if x2 <= x1 or y2 <= y1:
        logger.warning(f"Invalid bbox after clamping: {bbox} for {image_path}")
        return None, None

    # Crop face
    face_crop = img_rgb[y1:y2, x1:x2].copy()

    face_info = {
        "bbox": [int(x1), int(y1), int(x2), int(y2)],
        "det_score": float(primary_face.det_score),
        "landmarks": primary_face.kps.tolist() if primary_face.kps is not None else None,
    }

    logger.debug(f"Extracted face from {image_path}: bbox={face_info['bbox']}, score={face_info['det_score']:.3f}")
    return face_crop, face_info


# =============================================================================
# STAGE 2: DATA PREPROCESSING
# =============================================================================

def preprocess_face(face_crop: np.ndarray, target_size: tuple[int, int] = TARGET_SIZE) -> np.ndarray:
    """
    Resize face crop to target size (160, 160) using high-quality interpolation.

    Args:
        face_crop: Face crop as RGB numpy array (H, W, 3)
        target_size: Target (width, height) tuple

    Returns:
        Resized face as RGB numpy array (target_height, target_width, 3)
    """
    if face_crop.size == 0:
        raise ValueError("Empty face crop provided")

    # Use INTER_AREA for downsampling, INTER_CUBIC for upsampling
    h, w = face_crop.shape[:2]
    if h > target_size[1] or w > target_size[0]:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_CUBIC

    resized = cv2.resize(face_crop, target_size, interpolation=interpolation)
    return resized


# =============================================================================
# STAGE 3: DATA AUGMENTATION (Nested Loop - 30 variants per face)
# =============================================================================

def build_augmentation_pipeline() -> Any:
    """
    Build Albumentations pipeline with face-safe transforms.
    Only includes transformations that preserve structural identity.

    Returns:
        Albumentations Compose pipeline
    """
    try:
        import albumentations as A
    except ImportError as e:
        logger.error("albumentations not installed. Run: pip install albumentations")
        raise

    transforms = [
        A.HorizontalFlip(p=AUGMENTATION_CONFIG["horizontal_flip"]["p"]),
        A.RandomBrightnessContrast(
            brightness_limit=AUGMENTATION_CONFIG["brightness_contrast"]["brightness_limit"],
            contrast_limit=AUGMENTATION_CONFIG["brightness_contrast"]["contrast_limit"],
            p=AUGMENTATION_CONFIG["brightness_contrast"]["p"]
        ),
        A.Rotate(
            limit=AUGMENTATION_CONFIG["rotate"]["limit"],
            p=AUGMENTATION_CONFIG["rotate"]["p"],
            border_mode=cv2.BORDER_REFLECT_101
        ),
        A.GaussNoise(
            std_range=AUGMENTATION_CONFIG["gauss_noise"]["std_range"],
            p=AUGMENTATION_CONFIG["gauss_noise"]["p"]
        ),
    ]

    pipeline = A.Compose(transforms)
    logger.info("Albumentations pipeline built with face-safe transforms.")
    return pipeline


def augment_face(face_image: np.ndarray, pipeline: Any, num_augmentations: int = AUGMENTATIONS_PER_FACE) -> list[np.ndarray]:
    """
    Generate augmented variants of a face image using the augmentation pipeline.

    Args:
        face_image: Preprocessed face as RGB numpy array (H, W, 3)
        pipeline: Albumentations Compose pipeline
        num_augmentations: Number of augmented variants to generate

    Returns:
        List of augmented face images as RGB numpy arrays
    """
    augmented_faces = []

    for i in range(num_augmentations):
        # Apply augmentation
        augmented = pipeline(image=face_image)["image"]
        augmented_faces.append(augmented)

    logger.debug(f"Generated {len(augmented_faces)} augmented variants.")
    return augmented_faces


# =============================================================================
# STAGE 4: FACIAL FEATURE EXTRACTION (ArcFace R50 → 512-dim embeddings)
# =============================================================================

def extract_embeddings_batch(app: Any, face_batch: list[np.ndarray]) -> np.ndarray:
    """
    Extract 512-dimensional embeddings for a batch of face images using ArcFace R50.

    Uses the recognition model directly (``get_feat``) on each pre-cropped face —
    avoids re-running SCRFD detection on tight crops, which is unreliable and
    produced zero embeddings.

    Args:
        app: Initialized InsightFace FaceAnalysis instance
        face_batch: List of RGB face images (each H, W, 3)

    Returns:
        Embeddings array of shape (N, 512) where N = len(face_batch), L2-normalized
    """
    if not face_batch:
        return np.empty((0, EMBEDDING_DIM), dtype=np.float32)

    rec = app.models["recognition"]

    try:
        # Batch inference: single blobFromImages + one forward pass over all crops
        face_bgrs = [cv2.cvtColor(face_rgb, cv2.COLOR_RGB2BGR) for face_rgb in face_batch]
        embeddings = np.asarray(rec.get_feat(face_bgrs), dtype=np.float32).reshape(-1, EMBEDDING_DIM)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms < 1e-10] = 1.0
        embeddings = embeddings / norms
    except Exception as exc:
        logger.warning(f"Batched embedding extraction failed ({exc}); falling back per-crop")
        embeddings = []
        for face_rgb in face_batch:
            try:
                face_bgr = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2BGR)
                emb = np.asarray(rec.get_feat(face_bgr)).reshape(-1)
                norm = np.linalg.norm(emb)
                if norm > 1e-10:
                    emb = emb / norm
            except Exception:
                emb = np.zeros(EMBEDDING_DIM, dtype=np.float32)
            embeddings.append(emb)
        embeddings = np.stack(embeddings, axis=0).astype(np.float32)

    logger.debug(f"Extracted embeddings shape: {embeddings.shape}")
    return embeddings


# =============================================================================
# STAGE 5: GLOBAL DATA COMPILATION
# =============================================================================

class FacialPipeline:
    """
    End-to-end facial processing pipeline with nested-loop architecture.

    Loop structure:
        Outer  — iterate over 21 student subfolders
        Middle — iterate over ~34 images per student
        Inner  — generate 30 augmented variants per face
    """

    def __init__(self, input_dir: Path = INPUT_DIR):
        self.input_dir = input_dir
        self.app = None
        self.aug_pipeline = None

        # Master arrays for accumulation
        self.all_images: list[np.ndarray] = []
        self.all_embeddings: list[np.ndarray] = []
        self.all_labels: list[str] = []
        self.all_metadata: list[dict] = []

        # Global statistics
        self.stats = {
            "total_students": 0,
            "total_input_images": 0,
            "successfully_processed": 0,
            "failed_no_face": 0,
            "failed_corrupted": 0,
            "total_augmented_generated": 0,
            "total_embeddings_extracted": 0,
        }

        # Per-student breakdown
        self.per_student_stats: dict[str, dict] = {}

    def initialize(self) -> None:
        """Initialize all models and pipelines."""
        logger.info("=" * 60)
        logger.info("INITIALIZING FACIAL PIPELINE")
        logger.info("=" * 60)

        self.app = initialize_face_detector()
        self.aug_pipeline = build_augmentation_pipeline()

        logger.info("Pipeline initialization complete.\n")

    def process_single_image(self, image_path: Path, label: str) -> bool:
        """
        Process a single image through the complete pipeline.

        Args:
            image_path: Path to input image
            label: Label/metadata for this image (e.g., student_id or filename)

        Returns:
            True if successfully processed, False otherwise
        """
        logger.info(f"Processing: {image_path.name} | Label: {label}")

        # Stage 1: Face Extraction
        face_crop, face_info = extract_primary_face(self.app, str(image_path))
        if face_crop is None:
            self.stats["failed_no_face"] += 1
            return False

        # Stage 2: Preprocessing
        try:
            face_preprocessed = preprocess_face(face_crop, TARGET_SIZE)
        except Exception as e:
            logger.error(f"Preprocessing failed for {image_path.name}: {e}")
            self.stats["failed_corrupted"] += 1
            return False

        # Stage 3: Data Augmentation (Nested Loop - 30 variants)
        augmented_faces = augment_face(face_preprocessed, self.aug_pipeline, AUGMENTATIONS_PER_FACE)

        # Stage 4: Feature Extraction (Batch processing)
        embeddings = extract_embeddings_batch(self.app, augmented_faces)

        # Stage 5: Accumulate into master arrays
        for i, (aug_face, emb) in enumerate(zip(augmented_faces, embeddings)):
            self.all_images.append(aug_face)
            self.all_embeddings.append(emb)
            self.all_labels.append(label)
            self.all_metadata.append({
                "source_image": image_path.name,
                "student_id": label,
                "augmentation_index": i,
                "original_bbox": face_info["bbox"],
                "det_score": face_info["det_score"],
            })

        self.stats["successfully_processed"] += 1
        self.stats["total_augmented_generated"] += len(augmented_faces)
        self.stats["total_embeddings_extracted"] += len(embeddings)

        # Update per-student stats
        if label in self.per_student_stats:
            self.per_student_stats[label]["augmented_generated"] += len(augmented_faces)
            self.per_student_stats[label]["embeddings_extracted"] += len(embeddings)

        logger.info(f"  [OK] Generated {len(augmented_faces)} augmented faces | "
                    f"Embeddings: {embeddings.shape} | "
                    f"Det score: {face_info['det_score']:.3f}")

        return True

    def run(self) -> dict[str, Any]:
        """
        Execute the complete pipeline on all student subfolders.

        Loop structure:
            OUTER  — for each student folder (21 students)
            MIDDLE — for each image inside that folder (~34 images)
            INNER  — generate 30 augmented variants per face

        Returns:
            Dictionary containing final arrays and statistics
        """
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

        # Discover all student subdirectories
        student_folders = sorted([
            d for d in self.input_dir.iterdir()
            if d.is_dir()
        ])

        self.stats["total_students"] = len(student_folders)
        logger.info(f"Found {len(student_folders)} student folders in {self.input_dir}")

        if not student_folders:
            logger.error("No student folders found!")
            return self._compile_results()

        # === OUTER LOOP: iterate over each student ===
        for s_idx, student_dir in enumerate(student_folders, 1):
            student_id = student_dir.name

            # Gather images for this student
            image_files = sorted([
                f for f in student_dir.iterdir()
                if f.is_file() and f.suffix.lower() in image_extensions
            ])

            logger.info(f"\n[Student {s_idx}/{len(student_folders)}] {student_id} "
                        f"({len(image_files)} images)")

            # Initialize per-student stats
            self.per_student_stats[student_id] = {
                "total_images": len(image_files),
                "faces_detected": 0,
                "augmented_generated": 0,
                "embeddings_extracted": 0,
            }

            self.stats["total_input_images"] += len(image_files)

            if not image_files:
                logger.warning(f"  No images found in {student_dir}")
                continue

            # === MIDDLE LOOP: iterate over each image for this student ===
            for img_idx, img_path in enumerate(image_files, 1):
                logger.info(f"  [{img_idx}/{len(image_files)}] {img_path.name}")
                success = self.process_single_image(img_path, student_id)

                if success:
                    self.per_student_stats[student_id]["faces_detected"] += 1

            # Log per-student summary
            ps = self.per_student_stats[student_id]
            logger.info(f"  [Student-ok] {student_id}: {ps['faces_detected']}/{ps['total_images']} "
                        f"faces | {ps['augmented_generated']} augmented | "
                        f"{ps['embeddings_extracted']} embeddings")

        # Compile final results
        return self._compile_results()

    def _compile_results(self) -> dict[str, Any]:
        """Compile master arrays and return final results."""
        logger.info("\n" + "=" * 60)
        logger.info("COMPILING FINAL RESULTS")
        logger.info("=" * 60)

        # Convert lists to numpy arrays
        if self.all_images:
            images_array = np.stack(self.all_images, axis=0)
            embeddings_array = np.stack(self.all_embeddings, axis=0)
            labels_array = np.array(self.all_labels, dtype=object)
        else:
            images_array = np.empty((0, *TARGET_SIZE, 3), dtype=np.uint8)
            embeddings_array = np.empty((0, EMBEDDING_DIM), dtype=np.float32)
            labels_array = np.array([], dtype=object)

        # Log final shapes
        logger.info(f"\n{'='*60}")
        logger.info("FINAL ARRAY SHAPES (Structural Integrity Check)")
        logger.info(f"{'='*60}")
        logger.info(f"Images Matrix:     {images_array.shape}")
        logger.info(f"Feature Matrix:    {embeddings_array.shape}")
        logger.info(f"Labels Array:      {labels_array.shape}")
        logger.info(f"{'='*60}")

        # Log global statistics
        logger.info("\nGLOBAL PROCESSING STATISTICS:")
        logger.info(f"  Total students:           {self.stats['total_students']}")
        logger.info(f"  Total input images:       {self.stats['total_input_images']}")
        logger.info(f"  Successfully processed:   {self.stats['successfully_processed']}")
        logger.info(f"  Failed (no face detected):{self.stats['failed_no_face']}")
        logger.info(f"  Failed (corrupted/other): {self.stats['failed_corrupted']}")
        logger.info(f"  Total augmented generated:{self.stats['total_augmented_generated']}")
        logger.info(f"  Total embeddings extracted:{self.stats['total_embeddings_extracted']}")

        # Log per-student breakdown
        if self.per_student_stats:
            logger.info(f"\n{'='*60}")
            logger.info("PER-STUDENT BREAKDOWN")
            logger.info(f"{'='*60}")
            logger.info(f"{'Student ID':<18} {'Images':>7} {'Faces':>7} {'Aug':>8} {'Emb':>8}")
            logger.info(f"{'-'*18} {'-'*7} {'-'*7} {'-'*8} {'-'*8}")
            for sid, ps in self.per_student_stats.items():
                logger.info(f"{sid:<18} {ps['total_images']:>7} "
                            f"{ps['faces_detected']:>7} "
                            f"{ps['augmented_generated']:>8} "
                            f"{ps['embeddings_extracted']:>8}")

        # Verify structural integrity
        actual_total = len(self.all_images)
        logger.info(f"\nTotal samples in arrays: {actual_total}")

        return {
            "images": images_array,
            "embeddings": embeddings_array,
            "labels": labels_array,
            "metadata": self.all_metadata,
            "stats": self.stats,
            "per_student_stats": self.per_student_stats,
        }

    def save_results(self, results: dict[str, Any], output_dir: Path = Path("data/processed")) -> None:
        """
        Save compiled results to disk as .npz archive.

        Args:
            results: Dictionary from _compile_results()
            output_dir: Output directory path
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "facial_pipeline_results.npz"

        np.savez_compressed(
            output_path,
            images=results["images"],
            embeddings=results["embeddings"],
            labels=results["labels"],
            # metadata stored as JSON-serializable object array
            metadata=np.array(results["metadata"], dtype=object),
        )

        logger.info(f"\nResults saved to: {output_path}")
        logger.info(f"File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

    def save_augmented_images(self, output_dir: Path = Path("data/augmented")) -> None:
        """
        Export every generated augmented face as an individual .jpg file,
        organised by student → source image → augmentation index.

        Layout:
            data/augmented/<student_id>/<source_image_stem>/aug_<index>.jpg

        Args:
            output_dir: Root directory for the exported augmented images
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        saved = 0
        for meta, image in zip(self.all_metadata, self.all_images):
            student_dir = output_dir / meta["student_id"]
            source_dir = student_dir / Path(meta["source_image"]).stem
            source_dir.mkdir(parents=True, exist_ok=True)

            out_path = source_dir / f"aug_{meta['augmentation_index']:03d}.jpg"
            # Images stored as RGB arrays -> write as BGR for OpenCV
            cv2.imwrite(str(out_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            saved += 1

        logger.info(f"\nExported {saved} augmented face images to: {output_dir}")



# =============================================================================
# PARALLEL PROCESSING (workers over student folders)
# =============================================================================

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def _process_student_folder(student_id: str, input_dir: str,
                            intra_op_threads: int | None = None,
                            cv2_threads: int | None = None,
                            num_augmentations: int | None = None) -> dict[str, Any]:
    """
    Worker entry point (runs in a spawned process).

    Loads its own FaceAnalysis model + augmentation pipeline once, then processes
    every image in one student folder and returns the compiled arrays.

    Args:
        student_id: Name of the student subfolder.
        input_dir: Root directory containing student subfolders.
        intra_op_threads: Optional onnxruntime intra-op thread count override.
        cv2_threads: Optional OpenCV thread count override.
        num_augmentations: Optional augmentation count override.

    Returns:
        dict with keys: images (list), embeddings (np (N,512) float32),
        labels (list), metadata (list of dict), stats (dict)
    """
    global ONNX_INTRA_OP_THREADS, CV2_THREADS, AUGMENTATIONS_PER_FACE
    if intra_op_threads is not None:
        ONNX_INTRA_OP_THREADS = intra_op_threads
    if cv2_threads is not None:
        CV2_THREADS = cv2_threads
    if num_augmentations is not None:
        AUGMENTATIONS_PER_FACE = num_augmentations

    cv2.setNumThreads(CV2_THREADS)
    logger.info("[Worker][%s] starting subprocess", student_id)

    app = initialize_face_detector()
    aug_pipeline = build_augmentation_pipeline()

    student_dir = Path(input_dir) / student_id

    image_files = sorted([
        f for f in student_dir.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ])

    images: list[np.ndarray] = []
    embeddings: list[np.ndarray] = []
    labels: list[str] = []
    metadata: list[dict] = []

    stats = {
        "student_id": student_id,
        "total_images": len(image_files),
        "faces_detected": 0,
        "failed_no_face": 0,
        "failed_corrupted": 0,
        "augmented_generated": 0,
        "embeddings_extracted": 0,
    }

    for img_idx, img_path in enumerate(image_files, 1):
        face_crop, face_info = extract_primary_face(app, str(img_path))

        if face_crop is None:
            stats["failed_no_face"] += 1
            continue

        try:
            face_preprocessed = preprocess_face(face_crop, TARGET_SIZE)
        except Exception:
            stats["failed_corrupted"] += 1
            continue

        augmented_faces = augment_face(face_preprocessed, aug_pipeline, AUGMENTATIONS_PER_FACE)
        batch_embeddings = extract_embeddings_batch(app, augmented_faces)

        for i, (aug_face, emb) in enumerate(zip(augmented_faces, batch_embeddings)):
            images.append(aug_face)
            embeddings.append(emb)
            labels.append(student_id)
            metadata.append({
                "source_image": img_path.name,
                "student_id": student_id,
                "augmentation_index": i,
                "original_bbox": face_info["bbox"],
                "det_score": face_info["det_score"],
            })

        stats["faces_detected"] += 1
        stats["augmented_generated"] += len(augmented_faces)
        stats["embeddings_extracted"] += len(batch_embeddings)

        if img_idx % 5 == 0 or img_idx == len(image_files):
            logger.info("[Worker][%s] %d/%d images done",
                        student_id, img_idx, len(image_files))

    logger.info("[Worker][%s] finished: %d/%d faces | %d augmentations",
                student_id, stats["faces_detected"], stats["total_images"],
                stats["augmented_generated"])

    if embeddings:
        emb_array = np.stack(embeddings, axis=0).astype(np.float32)
    else:
        emb_array = np.empty((0, EMBEDDING_DIM), dtype=np.float32)

    return {
        "student_id": student_id,
        "images": images,
        "embeddings": emb_array,
        "labels": labels,
        "metadata": metadata,
        "stats": stats,
    }


def save_results_from_arrays(results: dict[str, Any], output_dir: Path = Path("data/processed")) -> None:
    """Save compiled master arrays to a .npz archive."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "facial_pipeline_results.npz"
    np.savez_compressed(
        output_path,
        images=results["images"],
        embeddings=results["embeddings"],
        labels=results["labels"],
        metadata=np.array(results["metadata"], dtype=object),
    )
    logger.info(f"Results saved to: {output_path}")
    logger.info(f"File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")


def save_augmented_from_arrays(results: dict[str, Any], output_dir: Path = Path("data/augmented")) -> None:
    """
    Export every augmented face as an individual .jpg, organised as
    data/augmented/<student_id>/<source_image_stem>/aug_<index>.jpg
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for image, meta in zip(results["images"], results["metadata"]):
        student_dir = output_dir / meta["student_id"]
        source_dir = student_dir / Path(meta["source_image"]).stem
        source_dir.mkdir(parents=True, exist_ok=True)
        out_path = source_dir / f"aug_{meta['augmentation_index']:03d}.jpg"
        cv2.imwrite(str(out_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        saved += 1
    logger.info(f"Exported {saved} augmented face images to: {output_dir}")


def run_parallel() -> dict[str, Any]:
    """Run the pipeline across student folders using a small process pool."""
    from concurrent.futures import ProcessPoolExecutor, as_completed

    student_folders = sorted([
        d.name for d in INPUT_DIR.iterdir()
        if d.is_dir()
    ])

    total_images = sum(len([
        f for f in (INPUT_DIR / sid).iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]) for sid in student_folders)

    logger.info(f"Parallel run: {len(student_folders)} students, "
                f"{total_images} images, {NUM_WORKER_PROCESSES} workers")

    all_images: list[np.ndarray] = []
    all_embeddings: list[np.ndarray] = []
    all_labels: list[str] = []
    all_metadata: list[dict] = []
    per_student_stats: dict[str, dict] = {}
    failed_students: list[tuple[str, str]] = []

    completed = 0
    with ProcessPoolExecutor(max_workers=NUM_WORKER_PROCESSES) as executor:
        futures = {executor.submit(_process_student_folder, sid, str(INPUT_DIR)): sid
                   for sid in student_folders}
        for future in as_completed(futures):
            sid = futures[future]
            try:
                result = future.result()
                all_images.extend(result["images"])
                all_embeddings.append(result["embeddings"])
                all_labels.extend(result["labels"])
                all_metadata.extend(result["metadata"])
                per_student_stats[sid] = result["stats"]
            except Exception as exc:
                logger.error(f"Student {sid} failed: {exc}")
                failed_students.append((sid, str(exc)))
            finally:
                completed += 1
                logger.info(f"Progress: {completed}/{len(student_folders)} students finished")

    images_array = np.stack(all_images, axis=0) if all_images else np.empty((0, *TARGET_SIZE, 3), dtype=np.uint8)
    embeddings_array = np.concatenate(all_embeddings, axis=0) if all_embeddings else np.empty((0, EMBEDDING_DIM), dtype=np.float32)
    labels_array = np.array(all_labels, dtype=object)

    logger.info(f"\n{'='*60}")
    logger.info("FINAL ARRAY SHAPES (Structural Integrity Check)")
    logger.info(f"{'='*60}")
    logger.info(f"Images Matrix:     {images_array.shape}")
    logger.info(f"Feature Matrix:    {embeddings_array.shape}")
    logger.info(f"Labels Array:      {labels_array.shape}")
    logger.info(f"{'='*60}")

    stats = {
        "total_students": len(student_folders),
        "total_input_images": total_images,
        "successfully_processed": sum(s["faces_detected"] for s in per_student_stats.values()),
        "failed_no_face": sum(s["failed_no_face"] for s in per_student_stats.values()),
        "failed_corrupted": sum(s["failed_corrupted"] for s in per_student_stats.values()),
        "total_augmented_generated": sum(s["augmented_generated"] for s in per_student_stats.values()),
        "total_embeddings_extracted": sum(s["embeddings_extracted"] for s in per_student_stats.values()),
    }

    for sid, err in failed_students:
        logger.error(f"FAILED STUDENT: {sid} -> {err}")

    logger.info("\nGLOBAL PROCESSING STATISTICS:")
    for k, v in stats.items():
        logger.info(f"  {k:<32} {v}")

    if per_student_stats:
        logger.info(f"\n{'='*60}")
        logger.info("PER-STUDENT BREAKDOWN")
        logger.info(f"{'='*60}")
        logger.info(f"{'Student ID':<18} {'Images':>7} {'Faces':>7} {'Aug':>8} {'Emb':>8}")
        for sid, ps in sorted(per_student_stats.items()):
            logger.info(f"{sid:<18} {ps['total_images']:>7} {ps['faces_detected']:>7} "
                        f"{ps['augmented_generated']:>8} {ps['embeddings_extracted']:>8}")

    return {
        "images": images_array,
        "embeddings": embeddings_array,
        "labels": labels_array,
        "metadata": all_metadata,
        "stats": stats,
        "per_student_stats": per_student_stats,
        "failed_students": failed_students,
    }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> None:
    """Main entry point for the facial pipeline script."""
    # Count student folders for banner
    student_folders = [d for d in INPUT_DIR.iterdir() if d.is_dir()] if INPUT_DIR.exists() else []

    logger.info("Starting End-to-End Facial Pipeline")
    logger.info(f"Dataset directory: {INPUT_DIR}")
    logger.info(f"Student folders:   {len(student_folders)}")
    logger.info(f"Target face size:  {TARGET_SIZE}")
    logger.info(f"Augmentations/face:{AUGMENTATIONS_PER_FACE}")

    # Verify input directory exists
    if not INPUT_DIR.exists():
        logger.error(f"Dataset directory does not exist: {INPUT_DIR}")
        sys.exit(1)

    # Initialize and run pipeline
    if NUM_WORKER_PROCESSES > 1:
        logger.info(f"Using parallel mode with {NUM_WORKER_PROCESSES} worker processes.")
        results = run_parallel()
    else:
        pipeline = FacialPipeline(INPUT_DIR)
        pipeline.initialize()
        results = pipeline.run()

    save_results_from_arrays(results)
    save_augmented_from_arrays(results)

    if results.get("failed_students"):
        logger.warning(f"WARNING: {len(results['failed_students'])} student(s) FAILED: "
                       f"{[sid for sid, _ in results['failed_students']]}")
    else:
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()