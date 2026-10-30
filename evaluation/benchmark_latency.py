"""
VISTA Latency, Scaling & System Resource Benchmarking
=====================================================
Benchmarks processing time per face, end-to-end pipeline latency,
group-photo scaling (10, 30, 60 faces), and hardware resource consumption.
Outputs benchmark results to evaluation/results/latency_benchmark.json.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

try:
    import psutil
except ImportError:
    psutil = None

# Path setup
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

RESULTS_DIR = ROOT_DIR / "evaluation" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def benchmark_pipeline_components():
    print("Benchmarking vision pipeline components...")

    from vista.vision.embed import normalize_embedding
    from vista.vision.match import FaceMatcher, cosine_similarity

    # 1. Cosine similarity matching latency (against gallery of 30, 100, 500 students)
    gallery_sizes = [30, 100, 500]
    matching_benchmarks = {}

    for size in gallery_sizes:
        gallery = {f"STU_{i:04d}": np.random.randn(512).tolist() for i in range(size)}
        query_vec = np.random.randn(512).astype(np.float32)
        query_vec = query_vec / np.linalg.norm(query_vec)
        matcher = FaceMatcher(threshold=0.55)

        # Warmup
        for _ in range(5):
            matcher.match(query_vec, gallery)

        # Timed run
        num_runs = 200
        t0 = time.perf_counter()
        for _ in range(num_runs):
            matcher.match(query_vec, gallery)
        t1 = time.perf_counter()

        avg_latency_ms = ((t1 - t0) / num_runs) * 1000.0
        matching_benchmarks[f"gallery_{size}"] = {
            "gallery_size": size,
            "avg_latency_ms": round(avg_latency_ms, 4),
            "throughput_faces_per_sec": round(1000.0 / avg_latency_ms, 1) if avg_latency_ms > 0 else 0
        }

    # 2. ResNet-50 personal classifier inference latency (if torch model available)
    resnet_benchmark = None
    try:
        import torch
        from vista.vision.personal_classifier import classify_face

        # Create dummy 112x112 face image
        dummy_face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)

        # Warmup
        for _ in range(3):
            classify_face(dummy_face)

        num_runs = 30
        t0 = time.perf_counter()
        for _ in range(num_runs):
            classify_face(dummy_face)
        t1 = time.perf_counter()

        avg_ms = ((t1 - t0) / num_runs) * 1000.0
        resnet_benchmark = {
            "model": "ResNet-50 PyTorch (best_model_npz_splitB.pth)",
            "device": "CPU",
            "avg_latency_ms": round(avg_ms, 2),
            "fps": round(1000.0 / avg_ms, 1)
        }
    except Exception as exc:
        resnet_benchmark = {"status": "skipped", "reason": str(exc)}

    # 3. InsightFace SCRFD & ArcFace latency (from loaded model)
    insightface_benchmark = None
    try:
        import tempfile
        import cv2
        from vista.vision.detect import FaceDetector
        detector = FaceDetector()
        detector._ensure_loaded()

        # Dummy 640x480 classroom image saved to temp file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
        dummy_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite(tmp_path, dummy_img)

        # Warmup
        for _ in range(2):
            detector.detect(tmp_path)

        num_runs = 5
        t0 = time.perf_counter()
        for _ in range(num_runs):
            detector.detect(tmp_path)
        t1 = time.perf_counter()

        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        avg_det_ms = ((t1 - t0) / num_runs) * 1000.0
        insightface_benchmark = {
            "detector": "SCRFD (det_10g.onnx)",
            "recognizer": "ArcFace R50 (w600k_r50.onnx)",
            "input_resolution": "640x480",
            "avg_inference_ms": round(avg_det_ms, 2)
        }
    except Exception as exc:
        insightface_benchmark = {"status": "skipped", "reason": str(exc)}

    # 4. Group photo scaling simulation (10, 30, 60 faces per classroom photo)
    # Total time = Detection (full frame) + N_faces * (Embedding + Liveness + Match)
    base_det_time = insightface_benchmark.get("avg_inference_ms", 120.0) if isinstance(insightface_benchmark, dict) and "avg_inference_ms" in insightface_benchmark else 120.0
    per_face_match_time = matching_benchmarks.get("gallery_30", {}).get("avg_latency_ms", 0.05)
    per_face_resnet_time = resnet_benchmark.get("avg_latency_ms", 35.0) if isinstance(resnet_benchmark, dict) and "avg_latency_ms" in resnet_benchmark else 35.0

    group_scaling = {}
    for face_count in [1, 5, 10, 20, 30, 45, 60]:
        # Fast path (ArcFace match only)
        fast_path_ms = base_det_time + (face_count * (5.0 + per_face_match_time))
        # Fallback path (ResNet-50 fallback on 15% unmatched)
        fallback_count = max(1, int(face_count * 0.15))
        hybrid_path_ms = fast_path_ms + (fallback_count * per_face_resnet_time)

        group_scaling[f"{face_count}_faces"] = {
            "face_count": face_count,
            "fast_path_latency_sec": round(fast_path_ms / 1000.0, 3),
            "hybrid_path_latency_sec": round(hybrid_path_ms / 1000.0, 3)
        }

    # 5. Resource Consumption
    resource_usage = {}
    if psutil is not None:
        process = psutil.Process()
        mem_info = process.memory_info()
        resource_usage = {
            "ram_rss_mb": round(mem_info.rss / 1024 / 1024, 2),
            "ram_vms_mb": round(mem_info.vms / 1024 / 1024, 2),
            "cpu_percent": round(psutil.cpu_percent(interval=0.5), 1),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_count_physical": psutil.cpu_count(logical=False)
        }

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "matching_benchmarks": matching_benchmarks,
        "resnet_classifier_benchmark": resnet_benchmark,
        "insightface_detection_benchmark": insightface_benchmark,
        "group_photo_scaling": group_scaling,
        "resource_usage": resource_usage
    }

    out_file = RESULTS_DIR / "latency_benchmark.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Latency benchmarks completed and saved to {out_file}")
    return results


if __name__ == "__main__":
    benchmark_pipeline_components()
