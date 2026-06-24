from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_URL = os.getenv("VISTA_DB_URL", "sqlite:///./vista_dev.db")

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    from .models import attendance, student, user, organization, intervention, audit  # noqa: F401
    Base.metadata.create_all(bind=engine)


def seed_demo_data(db: Session) -> None:
    """Insert one classroom, users, students, attendance, scores, and risk flags."""
    from .models.attendance import Attendance, Score, RiskFlag
    from .models.student import Classroom, Student
    from .models.user import User

    import bcrypt
    import uuid
    import random

    if db.query(Classroom).count() > 0:
        return

    now = datetime.now(timezone.utc).isoformat()

    classroom = Classroom(classroom_id="CSE-3A", name="CSE Third Year A")
    db.add(classroom)

    pw_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt(rounds=12)).decode()
    admin = User(
        id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@vista.local",
        password_hash=pw_hash,
        role="admin",
        is_active=True,
        created_at=now,
    )
    teacher_hash = bcrypt.hashpw(b"teacher123", bcrypt.gensalt(rounds=12)).decode()
    teacher = User(
        id=str(uuid.uuid4()),
        name="Demo Teacher",
        email="teacher@vista.local",
        password_hash=teacher_hash,
        role="teacher",
        is_active=True,
        created_at=now,
    )
    db.add_all([admin, teacher])

    students_data = [
        ("CS22B001", "Aarav Shah"),
        ("CS22B002", "Priya Nair"),
        ("CS22B003", "Rohan Mehta"),
        ("CS22B004", "Sneha Rao"),
        ("CS22B005", "Vikram Patel"),
    ]
    for sid, sname in students_data:
        db.add(Student(
            student_id=sid,
            name=sname,
            class_="CSE-3A",
            classroom_id="CSE-3A",
            is_active=True,
            enrolled_at="2025-08-01",
            created_at=now,
        ))

    db.flush()

    # --- Seed attendance for the past 8 weeks (Mon-Fri, 5 days/week) ---
    rng = random.Random(42)
    from datetime import timedelta

    base_date = datetime.now(timezone.utc).date() - timedelta(days=56)  # 8 weeks back

    # Attendance profiles: probability of being present
    att_profiles = {
        "CS22B001": 0.92,   # Good
        "CS22B002": 0.68,   # Borderline
        "CS22B003": 0.48,   # At risk
        "CS22B004": 0.88,   # Good
        "CS22B005": 0.72,   # Borderline
    }

    for day_offset in range(56):
        d = base_date + timedelta(days=day_offset)
        if d.weekday() >= 5:  # Skip weekends
            continue
        session_date = d.isoformat()
        for sid, prob in att_profiles.items():
            if rng.random() < prob:
                status = "present"
                confidence = round(rng.uniform(0.88, 0.99), 2)
            else:
                status = "absent"
                confidence = None
            # Only write a row if present (absent is derived at read time per API contract)
            if status == "present":
                db.add(Attendance(
                    id=str(uuid.uuid4()),
                    student_id=sid,
                    classroom_id="CSE-3A",
                    session_date=session_date,
                    timestamp=f"{session_date}T09:00:00Z",
                    status="present",
                    confidence=confidence,
                    is_manual_override=False,
                    created_at=now,
                ))

    # --- Seed scores (3 internal assessments) ---
    score_profiles = {
        "CS22B001": [78, 82, 80],
        "CS22B002": [62, 55, 48],
        "CS22B003": [42, 38, 32],
        "CS22B004": [72, 74, 76],
        "CS22B005": [68, 60, 54],
    }
    assessment_dates = [
        (base_date + timedelta(days=14)).isoformat(),
        (base_date + timedelta(days=28)).isoformat(),
        (base_date + timedelta(days=42)).isoformat(),
    ]
    for sid, scores in score_profiles.items():
        for i, score in enumerate(scores):
            db.add(Score(
                id=str(uuid.uuid4()),
                student_id=sid,
                subject="Data Structures",
                score=float(score),
                max_score=100.0,
                date=assessment_dates[i],
                created_at=now,
            ))

    # --- Seed risk flags via the actual ML engine ---
    try:
        from vista.ml.risk_engine import calculate_risk_from_metrics
        db.flush()

        for sid, _ in students_data:
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
            except Exception:
                pass
    except ImportError:
        pass

    db.commit()


# ---------------------------------------------------------------------------
# ML integration helper — called by ml/risk_engine._load_student_metrics()
# ---------------------------------------------------------------------------

def get_student_metrics(student_id: str, db: Session):
    """
    Build a StudentMetrics object from the DB for a given student_id.
    Raises ValueError if the student does not exist.
    """
    from .models.attendance import Attendance, Score
    from .models.student import Student
    from vista.ml.features import StudentMetrics

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None:
        raise ValueError(f"Student {student_id} not found")

    # Get all attendance records (present / liveness_failed) for the student
    att_rows = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id,
            Attendance.status.in_(["present", "liveness_failed"]),
        )
        .order_by(Attendance.session_date)
        .all()
    )

    # Total sessions = all sessions held for the classroom (unique session dates)
    all_sessions = (
        db.query(Attendance.session_date)
        .filter(Attendance.classroom_id == student.classroom_id)
        .distinct()
        .all()
    )
    # If no attendance rows exist for anyone, count from student's classroom sessions
    if not all_sessions:
        # Fallback: check all unique session_dates in the classroom
        total_sessions = 0
    else:
        total_sessions = len(all_sessions)

    # Sessions attended = present rows for this student
    sessions_attended = sum(1 for r in att_rows if r.status == "present")

    # Build full attendance sequence for consecutive absence calculation
    # For each session date, check if student was present
    session_dates_set = {row[0] for row in all_sessions}
    present_dates = {r.session_date for r in att_rows if r.status == "present"}

    attendance_sequence = []
    for d in sorted(session_dates_set):
        if d in present_dates:
            attendance_sequence.append("present")
        else:
            attendance_sequence.append("absent")

    from vista.ml.features import compute_consecutive_absences
    consecutive_absences = compute_consecutive_absences(attendance_sequence)

    # Group by ISO week to build weekly attendance percentages
    from collections import defaultdict
    week_buckets: dict[str, list[str]] = defaultdict(list)
    for d_str in sorted(session_dates_set):
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
            week_key = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
            status = "present" if d_str in present_dates else "absent"
            week_buckets[week_key].append(status)
        except ValueError:
            pass

    attendance_by_week: list[float] = []
    for week_key in sorted(week_buckets.keys()):
        statuses = week_buckets[week_key]
        pct = (statuses.count("present") / len(statuses)) * 100.0
        attendance_by_week.append(round(pct, 2))

    score_rows = (
        db.query(Score)
        .filter(Score.student_id == student_id)
        .order_by(Score.date)
        .all()
    )
    assessment_scores = [r.score for r in score_rows]
    assessment_max_scores = [r.max_score for r in score_rows]

    return StudentMetrics(
        student_id=student_id,
        total_sessions=total_sessions if total_sessions > 0 else len(att_rows),
        sessions_attended=sessions_attended,
        attendance_by_week=attendance_by_week,
        consecutive_absences=consecutive_absences,
        assessment_scores=assessment_scores,
        assessment_max_scores=assessment_max_scores,
        assignments_submitted=None,
        assignments_total=None,
    )
