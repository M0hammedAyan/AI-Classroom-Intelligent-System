"""
Root-level conftest for tests/ — seeds the shared test database before
tests/test_audit_fixes.py and tests/test_features_1_and_2.py run.

Must set VISTA_DB_URL before any app module is imported so the SQLAlchemy
engine picks up the test database path.
"""
import os
import sys

# Set the test DB URL before any app modules are imported.
os.environ["VISTA_DB_URL"] = "sqlite:///./test_vista.db"

# Ensure both import paths resolve to the same packages.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "vista", "backend")
for p in (ROOT_DIR, BACKEND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest

# Use the canonical vista.backend path so the engine/SessionLocal is the same
# module instance used by vista/backend/tests/conftest.py.
from vista.backend.app.db import engine, Base, SessionLocal, create_tables, seed_demo_data


@pytest.fixture(scope="session", autouse=True)
def seed_test_db_for_root_tests():
    """
    Full test DB setup for tests in tests/:
    1. Drop/create tables and seed base demo data.
    2. Create 7th-sem subjects + teacher accounts (without roster deactivation).
    3. Run the 7th-sem attendance+marks seed logic (subject_id-linked records).
    4. Insert the canonical 2026-10-30 face session for student 1DA24AI403.

    Does NOT call reconcile_current_roster() because that function deactivates
    CSE-3A demo students (CS22B001-CS22B005) by reading the App.jsx roster,
    which would break test_export.py and test_attendance.py tests.
    """
    Base.metadata.drop_all(bind=engine)
    create_tables()

    db = SessionLocal()
    try:
        seed_demo_data(db)
        _seed_7th_sem_curriculum(db)
        _run_demo_seed(db)
        _ensure_real_face_session(db)
    finally:
        db.close()

    yield


def _seed_7th_sem_curriculum(db):
    """
    Create the 7th-sem subjects, teacher accounts, and assignments.
    Does NOT touch student is_active flags.
    """
    import uuid
    import bcrypt
    from datetime import datetime, timezone
    from vista.backend.app.models.organization import ClassSection, Subject, TeacherSubjectAssignment
    from vista.backend.app.models.user import User

    now = datetime.now(timezone.utc).isoformat()

    class_section = db.query(ClassSection).filter(ClassSection.id == "class-aiml-4a").first()
    if class_section:
        class_section.code = "AIML-4A"
        class_section.name = "4th Year AIML"
        class_section.semester = "7"
    else:
        class_section = ClassSection(
            id="class-aiml-4a",
            code="AIML-4A",
            name="4th Year AIML",
            semester="7",
            created_at=now,
        )
        db.add(class_section)
    db.flush()

    subjects_config = [
        ("22AIU701",  "Deep Learning",                   "Rajeshwari",     "rajeshwari"),
        ("22AIU702",  "Generative AI",                   "Ajayprakash B V","ajayprakash"),
        ("22AIT703",  "Data Engineering and Analytics",  "Ganesh H J",     "ganesh"),
        ("22AIT704C", "Data Security and Privacy",       "Bharat V S",     "bharat"),
        ("22AIP706",  "Major Project Phase-II",          "Ganesh H J",     "ganesh"),
    ]

    teacher_cache: dict[str, User] = {}

    for code, name, faculty_name, login_name in subjects_config:
        subj = db.query(Subject).filter(Subject.code == code).first()
        if not subj:
            subj = Subject(
                id=f"subject-{code.lower()}",
                department_id="dept-aiml",
                name=name,
                code=code,
                semester="7",
                is_active=True,
                created_at=now,
            )
            db.add(subj)
        else:
            subj.name = name
            subj.is_active = True
        db.flush()

        teacher = teacher_cache.get(login_name)
        if teacher is None:
            teacher = db.query(User).filter(User.email == f"{login_name}@vista.local").first()
            if not teacher:
                teacher = User(
                    id=str(uuid.uuid4()),
                    name=faculty_name,
                    email=f"{login_name}@vista.local",
                    password_hash=bcrypt.hashpw(f"{login_name}123".encode(), bcrypt.gensalt(rounds=12)).decode(),
                    role="teacher",
                    school_id="school-cse",
                    department_id="dept-aiml",
                    is_active=True,
                    created_at=now,
                )
                db.add(teacher)
            else:
                teacher.name = faculty_name
                teacher.role = "teacher"
                teacher.is_active = True
            teacher_cache[login_name] = teacher
        db.flush()

        existing = db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == teacher.id,
            TeacherSubjectAssignment.subject_id == subj.id,
            TeacherSubjectAssignment.class_section_id == class_section.id,
        ).first()
        if existing:
            existing.is_active = True
        else:
            db.add(TeacherSubjectAssignment(
                id=str(uuid.uuid4()),
                teacher_id=teacher.id,
                subject_id=subj.id,
                class_section_id=class_section.id,
                assigned_at=now,
                is_active=True,
            ))

    db.commit()


def _run_demo_seed(db):
    """
    Inline equivalent of scripts/seed_demo_data.py.
    Seeds subject-linked attendance (source='seed') and CIE 1/2 marks for
    all students in the 4th Year AIML class, covering 2026-08-03 to 2026-10-31.
    Idempotent (deterministic uuid5 keys). Does not overwrite face/manual records.
    """
    import random
    import uuid
    from datetime import date, timedelta, datetime, timezone
    from vista.backend.app.models.student import Student
    from vista.backend.app.models.organization import Subject
    from vista.backend.app.models.attendance import Attendance, Score

    random.seed(42)

    SUBJECT_CODES = {
        "DL":      "22AIU701",
        "GAI":     "22AIU702",
        "DEA":     "22AIT703",
        "DSP":     "22AIT704C",
        "Project": "22AIP706",
    }
    TIMETABLE_PATTERN = {
        1: ["DL", "GAI", "DSP", "DEA", "Project"],
        2: ["GAI", "DSP", "DEA", "Project"],
        3: ["DEA", "DSP", "DL", "GAI"],
        4: ["DSP", "DEA", "DL", "Project"],
    }

    subjects_in_db = db.query(Subject).filter(Subject.is_active == True).all()
    subj_by_code = {s.code: s for s in subjects_in_db}
    for full_code in SUBJECT_CODES.values():
        if full_code not in subj_by_code:
            return  # Subjects not ready — skip.

    students = db.query(Student).filter(
        (Student.class_ == "4th Year AIML") | (Student.classroom_id == "class-aiml-4a")
    ).all()
    if not students:
        return

    student_baselines: dict[str, float] = {}
    for idx, s in enumerate(sorted(students, key=lambda x: x.student_id)):
        if idx in (3, 7, 14, 28, 45, 58):
            rate = round(random.uniform(0.55, 0.72), 2)
        elif idx % 5 == 0:
            rate = round(random.uniform(0.75, 0.82), 2)
        else:
            rate = round(random.uniform(0.83, 0.98), 2)
        student_baselines[s.student_id] = rate

    existing_real: set[tuple] = set()
    for r in db.query(Attendance).filter(Attendance.source.in_(["face", "manual"])).all():
        existing_real.add((r.student_id, r.session_date, r.subject_id))

    existing_seeded: set[tuple] = set()
    for r in db.query(Attendance.student_id, Attendance.session_date, Attendance.subject_id).filter(
        Attendance.source == "seed"
    ).all():
        existing_seeded.add((r[0], r[1], r[2]))

    now_iso = datetime.now(timezone.utc).isoformat()
    start_date = date(2026, 8, 3)
    end_date = date(2026, 10, 31)
    cur_date = start_date
    new_att = []

    while cur_date <= end_date:
        weekday = cur_date.weekday()
        if weekday in TIMETABLE_PATTERN:
            date_str = cur_date.isoformat()
            for short_code in TIMETABLE_PATTERN[weekday]:
                subj = subj_by_code[SUBJECT_CODES[short_code]]
                for student in students:
                    key = (student.student_id, date_str, subj.id)
                    code_key = (student.student_id, date_str, subj.code)
                    if key in existing_real or code_key in existing_real:
                        continue
                    if key in existing_seeded or code_key in existing_seeded:
                        continue
                    base_rate = student_baselines.get(student.student_id, 0.85)
                    is_present = random.random() < base_rate
                    rec_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{student.student_id}_{date_str}_{subj.id}"))
                    new_att.append(Attendance(
                        id=rec_id,
                        student_id=student.student_id,
                        classroom_id=student.classroom_id,
                        subject_id=subj.id,
                        session_date=date_str,
                        timestamp=f"{date_str}T09:30:00+00:00",
                        status="present" if is_present else "absent",
                        confidence=round(random.uniform(0.70, 0.98), 2) if is_present else None,
                        is_manual_override=False,
                        source="seed",
                        created_at=now_iso,
                    ))
        cur_date += timedelta(days=1)

    if new_att:
        db.bulk_save_objects(new_att)
        db.commit()

    # CIE 1 and CIE 2 marks.
    existing_scores: set[tuple] = set()
    for s in db.query(Score.student_id, Score.subject, Score.assessment_type).filter(
        Score.source == "seed"
    ).all():
        existing_scores.add((s[0], s[1], s[2]))

    new_scores = []
    for assessment_type, cie_date in [("CIE 1", "2026-09-18"), ("CIE 2", "2026-10-23")]:
        for s in students:
            base_pct = student_baselines.get(s.student_id, 0.85)
            for full_code in SUBJECT_CODES.values():
                subj = subj_by_code[full_code]
                score_key = (s.student_id, subj.name, assessment_type)
                if score_key in existing_scores:
                    continue
                rec_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{s.student_id}_{subj.id}_{assessment_type}"))
                is_absent = random.random() < 0.035
                if is_absent:
                    score_val, status = None, "absent"
                else:
                    raw = (base_pct * 22) + random.uniform(-4.0, 3.5)
                    score_val = round(max(0.0, min(25.0, raw)) * 2) / 2
                    status = "scored"
                new_scores.append(Score(
                    id=rec_id,
                    student_id=s.student_id,
                    subject=subj.name,
                    assessment_type=assessment_type,
                    score=score_val,
                    status=status,
                    max_score=25.0,
                    date=cie_date,
                    source="seed",
                    created_at=now_iso,
                ))

    if new_scores:
        db.bulk_save_objects(new_scores)
        db.commit()


def _ensure_real_face_session(db):
    """
    Insert the canonical 2026-10-30 Deep Learning face session for 1DA24AI403.
    This mirrors the real classroom session documented in CLAIMS_TABLE.md (C-15).
    """
    import uuid
    from datetime import datetime, timezone
    from vista.backend.app.models.attendance import Attendance
    from vista.backend.app.models.organization import Subject

    subj = db.query(Subject).filter(Subject.code == "22AIU701").first()
    if not subj:
        return

    session_date = "2026-10-30"
    student_id = "1DA24AI403"

    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.session_date == session_date,
        Attendance.subject_id == subj.id,
    ).first()
    if existing:
        return

    now_iso = datetime.now(timezone.utc).isoformat()
    db.add(Attendance(
        id=str(uuid.uuid4()),
        student_id=student_id,
        classroom_id="class-aiml-4a",
        subject_id=subj.id,
        session_date=session_date,
        timestamp=f"{session_date}T09:30:00+00:00",
        status="present",
        confidence=0.91,
        is_manual_override=False,
        source="face",
        created_at=now_iso,
    ))
    db.commit()
