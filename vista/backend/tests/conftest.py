"""
Pytest fixtures for VISTA API testing.
Uses in-memory SQLite and TestClient.
"""
import os
import pytest
from fastapi.testclient import TestClient

# Force test database
os.environ["VISTA_DB_URL"] = "sqlite:///./test_vista.db"

from vista.backend.app.main import app
from vista.backend.app.db import create_tables, SessionLocal, seed_demo_data, engine, Base


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create tables and seed once for all tests."""
    Base.metadata.drop_all(bind=engine)
    create_tables()
    db = SessionLocal()
    seed_demo_data(db)
    _seed_7th_sem_curriculum(db)
    db.close()
    yield
    engine.dispose()
    try:
        if os.path.exists("./test_vista.db"):
            os.remove("./test_vista.db")
    except PermissionError:
        pass  # Windows file lock — harmless


def _seed_7th_sem_curriculum(db):
    """
    Create the 7th-sem subjects, teacher accounts, and assignments needed by
    audit/feature tests. Does NOT touch student is_active flags (preserves
    CSE-3A demo students for export/attendance tests).
    """
    import uuid
    import bcrypt
    from datetime import datetime, timezone
    from vista.backend.app.models.organization import ClassSection, Subject, TeacherSubjectAssignment
    from vista.backend.app.models.user import User

    now = datetime.now(timezone.utc).isoformat()

    # Ensure the AIML-4A class section exists.
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

    # Subjects: (code, name, teacher_name, teacher_login)
    subjects_config = [
        ("22AIU701", "Deep Learning",                    "Rajeshwari",    "rajeshwari"),
        ("22AIU702", "Generative AI",                    "Ajayprakash B V","ajayprakash"),
        ("22AIT703", "Data Engineering and Analytics",   "Ganesh H J",    "ganesh"),
        ("22AIT704C","Data Security and Privacy",        "Bharat V S",    "bharat"),
        ("22AIP706", "Major Project Phase-II",           "Ganesh H J",    "ganesh"),
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

        # Teacher account
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

        # Assignment
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


@pytest.fixture
def client():
    """TestClient instance."""
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    """Get a fresh admin JWT token (not reused across tests)."""
    from vista.backend.app.routes.auth import _login_attempts, _blocklist
    _login_attempts.clear()
    _blocklist.clear()
    res = client.post("/api/v1/auth/login", json={"email": "admin@vista.local", "password": "admin123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["token"]


@pytest.fixture
def teacher_token(client):
    """Get a fresh teacher JWT token."""
    from vista.backend.app.routes.auth import _login_attempts, _blocklist
    _login_attempts.clear()
    _blocklist.clear()
    res = client.post("/api/v1/auth/login", json={"email": "teacher@vista.local", "password": "teacher123"})
    assert res.status_code == 200
    return res.json()["token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def teacher_headers(teacher_token):
    return {"Authorization": f"Bearer {teacher_token}"}
