"""
Celery Task Worker — Async Processing
=======================================
Offloads heavy operations from the request cycle:
- Face recognition (2s blocking → async)
- Batch risk recomputation
- PDF report generation

Start worker:
    celery -A vista.backend.app.tasks worker --loglevel=info

Requires Redis as broker:
    VISTA_REDIS_URL=redis://localhost:6379/0
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

from celery import Celery

REDIS_URL = os.getenv("VISTA_REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "vista",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 min max per task
)


@celery_app.task(name="vista.recognize_face")
def recognize_face_task(image_path: str) -> dict:
    """
    Async face recognition — offloads the ~2s blocking call.
    Returns: {student_id, confidence, liveness_passed}
    """
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

    from vista.vision.recognize import recognize
    result = recognize(image_path)
    return result


@celery_app.task(name="vista.recompute_risk_batch")
def recompute_risk_batch_task(student_ids: list[str]) -> dict:
    """
    Async batch risk recomputation.
    Computes risk for a list of students without blocking the API.
    """
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

    os.environ.setdefault("VISTA_DB_URL", "sqlite:///./vista_dev.db")
    from vista.backend.app.db import SessionLocal
    from vista.backend.app.models.student import Student
    from vista.backend.app.models.attendance import Attendance, Score, RiskFlag
    from vista.ml.risk_engine import calculate_risk_from_metrics
    from vista.backend.app.db import get_student_metrics

    db = SessionLocal()
    results = []
    errors = []
    now = datetime.now(timezone.utc).isoformat()

    try:
        for sid in student_ids:
            try:
                metrics = get_student_metrics(sid, db)
                result = calculate_risk_from_metrics(metrics)
                db.add(RiskFlag(
                    id=str(uuid.uuid4()),
                    student_id=sid,
                    risk_level=result["risk_level"].lower(),
                    reasons=json.dumps(result["reasons"]),
                    confidence=result["confidence"],
                    calculated_at=now,
                    created_at=now,
                ))
                results.append({"student_id": sid, "risk_level": result["risk_level"]})
            except Exception as exc:
                errors.append({"student_id": sid, "error": str(exc)})
        db.commit()
    finally:
        db.close()

    return {"computed": len(results), "errors": len(errors), "results": results}
