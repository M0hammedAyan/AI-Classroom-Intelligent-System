"""
Scheduled Tasks — APScheduler Integration
==========================================
Runs background tasks on a schedule:
- Nightly risk recomputation for all students
- Weekly attendance statistics aggregation

Usage:
    Called from main.py on startup. Runs in-process (not a separate worker).
    For production, consider Celery + Redis instead.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_scheduler = None


def init_scheduler():
    """Initialize and start the APScheduler if enabled via environment variable."""
    global _scheduler

    if os.getenv("VISTA_SCHEDULER_ENABLED", "false").lower() != "true":
        logger.info("Scheduler disabled. Set VISTA_SCHEDULER_ENABLED=true to enable.")
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.warning("APScheduler not installed. Scheduled tasks disabled.")
        return

    _scheduler = BackgroundScheduler()

    # Nightly risk recomputation at 2:00 AM
    _scheduler.add_job(
        recompute_all_risk_job,
        CronTrigger(hour=2, minute=0),
        id="nightly_risk_recompute",
        name="Nightly Risk Recomputation",
        replace_existing=True,
    )

    # Weekly stats aggregation on Monday at 6:00 AM
    _scheduler.add_job(
        weekly_stats_job,
        CronTrigger(day_of_week="mon", hour=6, minute=0),
        id="weekly_stats",
        name="Weekly Statistics Aggregation",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Scheduler started with 2 jobs: nightly_risk_recompute, weekly_stats")


def shutdown_scheduler():
    """Gracefully shut down the scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down.")


def recompute_all_risk_job():
    """Background job: recompute risk for all active students."""
    from .db import SessionLocal, get_student_metrics
    from .models.attendance import RiskFlag
    from .models.student import Student

    logger.info("Starting scheduled risk recomputation...")
    db = SessionLocal()
    try:
        from vista.ml.risk_engine import calculate_risk_from_metrics

        students = db.query(Student).filter(Student.is_active == True).all()
        now = datetime.now(timezone.utc).isoformat()
        computed = 0
        errors = 0

        for student in students:
            try:
                metrics = get_student_metrics(student.student_id, db)
                result = calculate_risk_from_metrics(metrics)
                flag = RiskFlag(
                    id=str(uuid.uuid4()),
                    student_id=student.student_id,
                    risk_level=result["risk_level"].lower(),
                    reasons=json.dumps(result["reasons"]),
                    confidence=result["confidence"],
                    calculated_at=now,
                    created_at=now,
                )
                db.add(flag)
                computed += 1
            except Exception as exc:
                logger.error(f"Risk compute failed for {student.student_id}: {exc}")
                errors += 1

        db.commit()
        logger.info(f"Risk recomputation complete: {computed} students, {errors} errors")

    except Exception as exc:
        logger.error(f"Scheduled risk recomputation failed: {exc}")
    finally:
        db.close()


def weekly_stats_job():
    """Background job: log weekly attendance summary."""
    from .db import SessionLocal
    from .models.attendance import Attendance
    from .models.student import Student

    logger.info("Running weekly attendance stats...")
    db = SessionLocal()
    try:
        from datetime import timedelta
        today = datetime.now(timezone.utc).date()
        week_ago = (today - timedelta(days=7)).isoformat()
        today_str = today.isoformat()

        total_students = db.query(Student).filter(Student.is_active == True).count()
        total_present = (
            db.query(Attendance)
            .filter(
                Attendance.session_date >= week_ago,
                Attendance.session_date <= today_str,
                Attendance.status == "present",
            )
            .count()
        )

        logger.info(f"Weekly stats: {total_present} attendance records, {total_students} active students")
    except Exception as exc:
        logger.error(f"Weekly stats failed: {exc}")
    finally:
        db.close()
