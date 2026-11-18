"""Developer mode: dry-run face recognition with no class/subject/period checks.

Enabled only when the server is started with VISTA_DEV_MODE=1. Nothing is
written to the database; requests are logged to the server log only.

Each face is returned with its bounding box ([x1, y1, x2, y2] integers in the
pixels of the image as OpenCV decodes it, i.e. with EXIF orientation applied,
clamped to the image) and a status: recognized, below_threshold or unknown.
"""
from __future__ import annotations

import base64
import logging
import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.student import Student
from ..routes.attendance import MAX_IMAGE_BYTES, _call_vision_all
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/dev", tags=["dev"])
logger = logging.getLogger("vista.dev")

# A rejected candidate scoring below this is shown as "unknown" instead of "below_threshold".
# Display only: it has no effect on whether a face is accepted.
CANDIDATE_FLOOR = 0.30


def _image_size(path: str) -> tuple[int | None, int | None]:
    """Width and height of the image as the detector decodes it (EXIF orientation applied)."""
    import cv2

    img = cv2.imread(path)
    if img is None:
        return None, None
    height, width = img.shape[:2]
    return int(width), int(height)


def _clamp_bbox(bbox, width, height) -> list[int] | None:
    if not bbox or len(bbox) < 4:
        return None
    x1, y1, x2, y2 = (int(round(float(v))) for v in bbox[:4])
    if width is not None and height is not None:
        x1, x2 = max(0, min(x1, width)), max(0, min(x2, width))
        y1, y2 = max(0, min(y1, height)), max(0, min(y2, height))
    return [x1, y1, x2, y2]


def dev_mode_enabled() -> bool:
    """Read the flag at request time so it cannot be changed from the browser."""
    return os.getenv("VISTA_DEV_MODE", "").strip().lower() in {"1", "true", "yes", "on"}


class DevRecognizeRequest(BaseModel):
    image: str  # base64-encoded JPEG or PNG


@router.get("/status")
def dev_status():
    return {"enabled": dev_mode_enabled()}


@router.post("/recognize")
def dev_recognize(
    body: DevRecognizeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not dev_mode_enabled():
        raise HTTPException(status_code=403, detail={"code": "DEV_MODE_DISABLED", "message": "Developer mode is not enabled on this server."})
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Developer mode requires admin or teacher role."})

    try:
        image_bytes = base64.b64decode(body.image)
    except Exception:
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": "Image must be valid base64."})
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail={"code": "UPLOAD_TOO_LARGE", "message": "Image exceeds 30 MB limit."})

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name
        image_width, image_height = _image_size(tmp_path)
        vision_results = _call_vision_all(tmp_path, skip_liveness=True, dedupe=False, include_bbox=True)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    def _name(student_id):
        if not student_id:
            return None
        student = db.query(Student).filter(Student.student_id == student_id).first()
        return student.name if student else None

    results = []
    for index, r in enumerate(vision_results, start=1):
        sid = r.get("student_id")
        cid = r.get("candidate_id")
        cscore = r.get("candidate_score")
        if sid:
            status = "recognized"
        elif cid and cscore is not None and float(cscore) >= CANDIDATE_FLOOR:
            status = "below_threshold"
        else:
            status = "unknown"
        item = {
            "index": index,
            "status": status,
            "student_id": sid,
            "student_name": _name(sid),
            "confidence": float(r.get("confidence", 0.0)),
            "decided_by": r.get("decided_by"),
            "bbox": _clamp_bbox(r.get("bbox"), image_width, image_height),
        }
        if status == "below_threshold":
            item["candidate_id"] = cid
            item["candidate_name"] = _name(cid)
            item["candidate_score"] = float(cscore)
            item["candidate_source"] = r.get("candidate_source")
        results.append(item)

    logger.info(
        "DEV recognize (dry run, nothing saved): user=%s role=%s faces=%d",
        current_user.id, current_user.role, len(results),
    )
    return {
        "dry_run": True,
        "faces_detected": len(results),
        "image_width": image_width,
        "image_height": image_height,
        "results": results,
    }
