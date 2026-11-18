"""Developer mode (VISTA_DEV_MODE) endpoint tests: flag off and flag on."""
import base64
from datetime import datetime, timezone

import pytest

MINIMAL_PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n").decode()
FAKE_FACES = [
    {"student_id": "1DA22AI402", "confidence": 0.93, "liveness_passed": True, "decided_by": "gallery"},
    {"student_id": None, "confidence": 0.41, "liveness_passed": True, "decided_by": None},
]


def _counts():
    from vista.backend.app.db import SessionLocal
    from vista.backend.app.models.attendance import Attendance
    from vista.backend.app.models.capture import CaptureEvent
    db = SessionLocal()
    try:
        return db.query(Attendance).count(), db.query(CaptureEvent).count()
    finally:
        db.close()


@pytest.fixture
def student_headers():
    from vista.backend.app.db import SessionLocal
    from vista.backend.app.models.user import User
    from vista.backend.app.routes.auth import _make_jwt
    db = SessionLocal()
    user = User(
        id="dev-test-student", name="Dev Test Student", email="dev-test-student@vista.local",
        password_hash="x", role="student", is_active=True,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(user)
    db.commit()
    yield {"Authorization": f"Bearer {_make_jwt(user.id, 'student')}"}
    db.delete(user)
    db.commit()
    db.close()


@pytest.fixture
def vision_calls(monkeypatch):
    from vista.backend.app.routes import dev
    calls = []

    def fake(path, skip_liveness=False, dedupe=True):
        calls.append(skip_liveness)
        return FAKE_FACES

    monkeypatch.setattr(dev, "_call_vision_all", fake)
    return calls


# ---------------------------------------------------------------- flag OFF
def test_dev_status_off_by_default(client, monkeypatch):
    monkeypatch.delenv("VISTA_DEV_MODE", raising=False)
    res = client.get("/api/v1/dev/status")
    assert res.status_code == 200
    assert res.json() == {"enabled": False}


@pytest.mark.parametrize("who", ["admin_headers", "teacher_headers"])
def test_dev_recognize_refused_when_off(client, monkeypatch, vision_calls, request, who):
    monkeypatch.delenv("VISTA_DEV_MODE", raising=False)
    headers = request.getfixturevalue(who)
    res = client.post("/api/v1/dev/recognize", headers=headers, json={"image": MINIMAL_PNG})
    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "DEV_MODE_DISABLED"
    assert vision_calls == []


def test_dev_recognize_requires_auth(client, monkeypatch):
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    res = client.post("/api/v1/dev/recognize", json={"image": MINIMAL_PNG})
    assert res.status_code == 401


def test_mark_batch_still_requires_scope_fields_when_off(client, monkeypatch, admin_headers):
    monkeypatch.delenv("VISTA_DEV_MODE", raising=False)
    res = client.post("/api/v1/attendance/mark-batch", headers=admin_headers, json={"image": MINIMAL_PNG})
    assert res.status_code == 422  # classroom_id and session_date are still required


def test_mark_batch_unchanged_by_dev_flag_on(client, monkeypatch, admin_headers):
    """Even with the flag on, the normal endpoint keeps its required fields."""
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    res = client.post("/api/v1/attendance/mark-batch", headers=admin_headers, json={"image": MINIMAL_PNG})
    assert res.status_code == 422


# ---------------------------------------------------------------- flag ON
def test_dev_status_on(client, monkeypatch):
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    assert client.get("/api/v1/dev/status").json() == {"enabled": True}


@pytest.mark.parametrize("who", ["admin_headers", "teacher_headers"])
def test_dev_recognize_allowed_for_admin_and_teacher(client, monkeypatch, vision_calls, request, who):
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    headers = request.getfixturevalue(who)
    before = _counts()
    # Only the image is sent: no classroom, subject, period or date.
    res = client.post("/api/v1/dev/recognize", headers=headers, json={"image": MINIMAL_PNG})
    assert res.status_code == 200
    body = res.json()
    assert body["dry_run"] is True
    assert body["faces_detected"] == 2
    assert body["results"][0]["student_id"] == "1DA22AI402"
    assert body["results"][0]["confidence"] == 0.93
    assert body["results"][0]["decided_by"] == "gallery"
    assert body["results"][1]["student_id"] is None
    assert vision_calls == [True]  # liveness skipped
    assert _counts() == before  # nothing written


def test_dev_recognize_returns_known_student_name(client, monkeypatch, admin_headers):
    from vista.backend.app.routes import dev
    from vista.backend.app.db import SessionLocal
    from vista.backend.app.models.student import Student
    db = SessionLocal()
    known = db.query(Student).first()
    known_id, known_name = known.student_id, known.name
    db.close()
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    monkeypatch.setattr(dev, "_call_vision_all", lambda p, skip_liveness=False, dedupe=True: [
        {"student_id": known_id, "confidence": 0.9, "liveness_passed": True, "decided_by": "classifier"}])
    res = client.post("/api/v1/dev/recognize", headers=admin_headers, json={"image": MINIMAL_PNG})
    assert res.json()["results"][0]["student_name"] == known_name


def test_dev_recognize_refused_for_student(client, monkeypatch, vision_calls, student_headers):
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    res = client.post("/api/v1/dev/recognize", headers=student_headers, json={"image": MINIMAL_PNG})
    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "FORBIDDEN"
    assert vision_calls == []


def test_dev_recognize_no_duplicate_filtering(client, monkeypatch, admin_headers, vision_calls):
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    for _ in range(2):
        res = client.post("/api/v1/dev/recognize", headers=admin_headers, json={"image": MINIMAL_PNG})
        assert res.json()["faces_detected"] == 2


def test_dev_recognize_rejects_invalid_base64(client, monkeypatch, admin_headers):
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    res = client.post("/api/v1/dev/recognize", headers=admin_headers, json={"image": "***not base64***"})
    assert res.status_code == 400
    assert res.json()["detail"]["code"] == "INVALID_IMAGE"


def test_dev_recognize_passes_dedupe_off_and_returns_same_student_twice(client, monkeypatch, admin_headers):
    from vista.backend.app.routes import dev
    seen = {}
    def fake(path, skip_liveness=False, dedupe=True):
        seen["dedupe"] = dedupe
        return [{"student_id": "X1", "confidence": 0.9, "liveness_passed": True, "decided_by": "gallery"},
                {"student_id": "X1", "confidence": 0.7, "liveness_passed": True, "decided_by": "classifier"}]
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    monkeypatch.setattr(dev, "_call_vision_all", fake)
    res = client.post("/api/v1/dev/recognize", headers=admin_headers, json={"image": MINIMAL_PNG})
    assert seen["dedupe"] is False
    assert [r["confidence"] for r in res.json()["results"]] == [0.9, 0.7]


def test_recognize_all_dedupe_flag(monkeypatch):
    import importlib
    rec = importlib.import_module("vista.vision.recognize")
    class Det:
        def detect(self, p):
            return [{"bbox": [0, 0, 1, 1]}, {"bbox": [0, 0, 1, 1]}]
    monkeypatch.setattr(rec, "get_detector", lambda: Det())
    monkeypatch.setattr(rec, "_classify_detected_face", lambda p, f: {"student_id": "X1", "confidence": 0.8})
    assert len(rec.recognize_all("x.jpg", skip_liveness=True, dedupe=False)) == 2
    assert len(rec.recognize_all("x.jpg", skip_liveness=True)) == 1

