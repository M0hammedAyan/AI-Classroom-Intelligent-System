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
    db.close()
    yield
    engine.dispose()
    try:
        if os.path.exists("./test_vista.db"):
            os.remove("./test_vista.db")
    except PermissionError:
        pass  # Windows file lock — harmless


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
