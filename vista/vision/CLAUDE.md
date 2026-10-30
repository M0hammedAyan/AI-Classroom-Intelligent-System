# CLAUDE.md — vision/ (Member 1: Face Recognition & Attendance Engine)

## Project Context
VISTA is a 4-person college MVP: face-recognition attendance + academic risk flagging.
**Current scope: pilot only — one classroom, 20–30 students.** This is NOT the 80–100
student / multi-college spec from the original report. Do not expand scope without an
explicit instruction.

The team works in parallel against a frozen contract in `docs/API_CONTRACT.md` and
`docs/DB_SCHEMA.md`. Those files are the source of truth — if anything here conflicts
with them, the docs win and the team gets notified.

## Your Module's Job
Detect and recognize student faces from a captured image, return a structured result.
This module is standalone — it does not know about the API, the database, or the
frontend. Backend (Member 2) imports your function; you don't import anything from them.

## Entry Point Contract
```python
# vision/recognize.py
def recognize(
    image_path: str,
    gallery: dict[str, list[np.ndarray]] | None = None,
    match_threshold: float = 0.55,
) -> list[dict]:
    """
    Returns list of detected face matches:
    [
        {
            "student_id": str | None,   # None if unmatched
            "confidence": float,         # 0.0–1.0 (cosine similarity or softmax prob)
            "liveness_passed": bool,     # Heuristic texture/geometry anti-spoofing
            "method": str,               # "arcface" or "personal_classifier"
            "bbox": list[int],           # [x1, y1, x2, y2]
        },
        ...
    ]
    """
```

## Pipeline Files
- `detect.py` — Face detection via InsightFace SCRFD (`buffalo_l`)
- `embed.py` — ArcFace R50 512-dim feature extraction and normalization
- `match.py` — Cosine similarity matching (default threshold 0.55, env `VISTA_FACE_MATCH_THRESHOLD`)
- `personal_classifier.py` — PyTorch ResNet-50 classifier trained on `.npz` (`best_model_npz_splitB.pth`, 90.10% accuracy)
- `tracker.py` — Multi-frame greedy IoU track manager
- `liveness.py` — Heuristic anti-spoofing (detection confidence, box dimensions, Laplacian texture variance)
- `recognize.py` — Pipeline orchestrator (checks ArcFace gallery first, invokes personal classifier if unmatched)
- `enroll.py` — Extracts and averages embeddings from 3–5 enrollment images
- `facial_pipeline.py` — End-to-end processing script
- `tests/test_recognize.py` — Automated test suite (7 tests)

## Hard Rules
- Use pretrained models. No training a recognition model from scratch — no dataset or
  compute budget for that.
- Test set must be separate from enrollment images (different day/session), or accuracy
  numbers are meaningless.
- Report precision, recall, and false-accept rate separately — not just "accuracy."
  False-accept (marking the wrong student present) is the dangerous failure mode.
- Log real test results in `docs/INTEGRATION_LOG.md` so the team has honest numbers,
  not optimistic ones.

## Explicitly Out of Scope Right Now
- RealSense/depth-camera-based liveness — 2D face recognition only for the pilot
- Multi-camera / PTZ tracking
- Edge device deployment (Raspberry Pi/Jetson) — runs on a dev laptop for now
- Training or fine-tuning embedding models

## File/Naming Conventions
snake_case for all Python files and function names.

---

## Agent Response Convention

After completing any task in this module, always end your response with this block:

**Built:** [1–2 sentences — what was just implemented or changed in `vision/`]  
**Next:** [1–2 specific actionable next steps for this module]

Keep it short. One short paragraph maximum per section. No long summaries unless the user explicitly asks for one.
