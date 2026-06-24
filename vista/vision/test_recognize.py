"""
Vision Module — Integration Tests
==================================
Tests the face recognition pipeline against known images.

Run from project root:
    python -m vista.vision.test_recognize

For full testing, enrollment photos must exist. This test suite includes:
1. Module import test
2. Detector initialization test
3. Face detection on a sample image (if available)
4. Matching logic unit tests (no model needed)
5. Liveness heuristic tests
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

PASS = "✓"
FAIL = "✗"


def _check(condition: bool, msg: str) -> bool:
    mark = PASS if condition else FAIL
    status = "PASS" if condition else "FAIL"
    print(f"  {mark} [{status}] {msg}")
    return condition


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Test 1: Module imports
# ---------------------------------------------------------------------------

def test_imports() -> bool:
    _section("Test 1 — Module Imports")
    try:
        from vista.vision.detect import FaceDetector, get_detector
        from vista.vision.embed import normalize_embedding, average_embeddings
        from vista.vision.match import FaceMatcher, cosine_similarity
        from vista.vision.liveness import check_liveness
        from vista.vision.recognize import recognize
        return _check(True, "All vision module imports successful")
    except ImportError as exc:
        return _check(False, f"Import failed: {exc}")


# ---------------------------------------------------------------------------
# Test 2: Cosine similarity correctness
# ---------------------------------------------------------------------------

def test_cosine_similarity() -> bool:
    _section("Test 2 — Cosine Similarity")
    from vista.vision.match import cosine_similarity

    # Identical vectors → similarity = 1.0
    a = np.array([1.0, 0.0, 0.0])
    a = a / np.linalg.norm(a)
    sim = cosine_similarity(a, a)
    ok1 = _check(abs(sim - 1.0) < 1e-6, f"Identical vectors: sim={sim:.6f} (expected 1.0)")

    # Orthogonal vectors → similarity = 0.0
    b = np.array([0.0, 1.0, 0.0])
    b = b / np.linalg.norm(b)
    sim = cosine_similarity(a, b)
    ok2 = _check(abs(sim) < 1e-6, f"Orthogonal vectors: sim={sim:.6f} (expected 0.0)")

    # Opposite vectors → similarity = -1.0
    c = -a
    sim = cosine_similarity(a, c)
    ok3 = _check(abs(sim + 1.0) < 1e-6, f"Opposite vectors: sim={sim:.6f} (expected -1.0)")

    return ok1 and ok2 and ok3


# ---------------------------------------------------------------------------
# Test 3: Face Matcher logic
# ---------------------------------------------------------------------------

def test_matcher() -> bool:
    _section("Test 3 — Face Matcher Logic")
    from vista.vision.match import FaceMatcher

    matcher = FaceMatcher(threshold=0.55)

    # Create synthetic gallery
    emb_a = np.random.randn(512).astype(np.float32)
    emb_a = emb_a / np.linalg.norm(emb_a)

    emb_b = np.random.randn(512).astype(np.float32)
    emb_b = emb_b / np.linalg.norm(emb_b)

    gallery = {
        "CS22B001": emb_a.tolist(),
        "CS22B002": emb_b.tolist(),
    }

    # Exact match for student A
    result = matcher.match(emb_a, gallery)
    ok1 = _check(result["student_id"] == "CS22B001", f"Exact match: {result['student_id']} (expected CS22B001)")
    ok2 = _check(result["matched"] is True, f"matched=True (sim={result['similarity']:.4f})")

    # Unknown face (random embedding unlikely to match)
    unknown = np.random.randn(512).astype(np.float32)
    unknown = unknown / np.linalg.norm(unknown)
    result = matcher.match(unknown, gallery)
    ok3 = _check(result["similarity"] < 0.55, f"Unknown face: sim={result['similarity']:.4f} (below threshold)")

    # Empty gallery
    result = matcher.match(emb_a, {})
    ok4 = _check(result["student_id"] is None, "Empty gallery returns None")

    return ok1 and ok2 and ok3 and ok4


# ---------------------------------------------------------------------------
# Test 4: Embedding utilities
# ---------------------------------------------------------------------------

def test_embeddings() -> bool:
    _section("Test 4 — Embedding Utilities")
    from vista.vision.embed import normalize_embedding, average_embeddings, embedding_to_list, list_to_embedding

    # Normalize
    raw = np.array([3.0, 4.0, 0.0])
    normed = normalize_embedding(raw)
    ok1 = _check(abs(np.linalg.norm(normed) - 1.0) < 1e-6, "Normalization produces unit vector")

    # Average embeddings
    embs = [np.ones(512) / np.sqrt(512), np.ones(512) / np.sqrt(512)]
    avg = average_embeddings(embs)
    ok2 = _check(abs(np.linalg.norm(avg) - 1.0) < 1e-6, "Average embedding is normalized")

    # Round-trip serialization
    original = np.random.randn(512).astype(np.float32)
    original = original / np.linalg.norm(original)
    as_list = embedding_to_list(original)
    restored = list_to_embedding(as_list)
    diff = np.max(np.abs(original - restored))
    ok3 = _check(diff < 1e-5, f"Serialization round-trip: max diff = {diff:.2e}")

    return ok1 and ok2 and ok3


# ---------------------------------------------------------------------------
# Test 5: Liveness heuristics
# ---------------------------------------------------------------------------

def test_liveness() -> bool:
    _section("Test 5 — Liveness Heuristics")
    from vista.vision.liveness import check_liveness

    # High confidence, large face → should pass
    face_good = {"det_score": 0.95, "bbox": [100, 100, 300, 300]}
    result = check_liveness(face_good)
    ok1 = _check(result["liveness_passed"] is True, f"Good face passes liveness (score={result['liveness_score']:.2f})")

    # Low confidence → should fail
    face_bad = {"det_score": 0.3, "bbox": [100, 100, 300, 300]}
    result = check_liveness(face_bad)
    ok2 = _check(result["liveness_passed"] is False, f"Low confidence fails liveness (score={result['liveness_score']:.2f})")

    # Tiny face → should fail
    face_tiny = {"det_score": 0.9, "bbox": [100, 100, 130, 130]}
    result = check_liveness(face_tiny)
    ok3 = _check(result["liveness_passed"] is False, f"Tiny face fails liveness")

    return ok1 and ok2 and ok3


# ---------------------------------------------------------------------------
# Test 6: InsightFace model loading (requires model downloaded)
# ---------------------------------------------------------------------------

def test_model_loading() -> bool:
    _section("Test 6 — InsightFace Model Loading")
    try:
        from vista.vision.detect import FaceDetector
        detector = FaceDetector()
        detector._ensure_loaded()
        ok = _check(detector._app is not None, "InsightFace model loaded successfully")
        return ok
    except Exception as exc:
        _check(False, f"Model loading failed: {exc}")
        print("  → This is expected if the model hasn't finished downloading.")
        print("  → Run: python -c \"from insightface.app import FaceAnalysis; FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider']).prepare(ctx_id=-1)\"")
        return False


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nVISTA Vision Module — Test Suite")
    print("Face Recognition Pipeline | Integration Tests")

    tests = [
        ("Imports", test_imports),
        ("Cosine Similarity", test_cosine_similarity),
        ("Face Matcher", test_matcher),
        ("Embedding Utils", test_embeddings),
        ("Liveness Heuristics", test_liveness),
        ("Model Loading", test_model_loading),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
            else:
                failed += 1
        except Exception as exc:
            print(f"  {FAIL} [ERROR] {name} raised: {exc}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"  Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)


if __name__ == "__main__":
    main()
