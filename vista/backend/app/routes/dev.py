"""Developer mode: dry-run face recognition with no class/subject/period checks.

Enabled only when the server is started with VISTA_DEV_MODE=1. Nothing is
written to the database; requests are logged to the server log only.
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
        vision_results = _call_vision_all(tmp_path, skip_liveness=True, dedupe=False)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    results = []
    for r in vision_results:
        sid = r.get("student_id")
        student = db.query(Student).filter(Student.student_id == sid).first() if sid else None
        results.append({
            "student_id": sid,
            "student_name": student.name if student else None,
            "confidence": float(r.get("confidence", 0.0)),
            "decided_by": r.get("decided_by"),
        })

    logger.info(
        "DEV recognize (dry run, nothing saved): user=%s role=%s faces=%d",
        current_user.id, current_user.role, len(results),
    )
    return {"dry_run": True, "faces_detected": len(results), "results": results}
