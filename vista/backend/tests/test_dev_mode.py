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

    def fake(path, skip_liveness=False, dedupe=True, include_bbox=False):
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
    monkeypatch.setattr(dev, "_call_vision_all", lambda p, skip_liveness=False, dedupe=True, include_bbox=False: [
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
    def fake(path, skip_liveness=False, dedupe=True, include_bbox=False):
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
    monkeypatch.setattr(rec, "_classify_detected_face", lambda p, f, with_candidate=False: {"student_id": "X1", "confidence": 0.8})
    assert len(rec.recognize_all("x.jpg", skip_liveness=True, dedupe=False)) == 2
    assert len(rec.recognize_all("x.jpg", skip_liveness=True)) == 1


# ---------------------------------------------------------------- bounding boxes
def _fake_faces(monkeypatch, faces, size=(640, 480)):
    from vista.backend.app.routes import dev
    seen = {}

    def fake(path, skip_liveness=False, dedupe=True, include_bbox=False):
        seen["include_bbox"] = include_bbox
        return faces

    monkeypatch.setattr(dev, "_call_vision_all", fake)
    monkeypatch.setattr(dev, "_image_size", lambda path: size)
    return seen


def test_dev_recognize_returns_clamped_integer_bboxes_and_image_size(client, monkeypatch, admin_headers):
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    seen = _fake_faces(monkeypatch, [
        {"student_id": "S1", "confidence": 0.9, "bbox": [10.4, 20.6, 110.2, 140.9], "decided_by": "gallery"},
        {"student_id": None, "confidence": 0.1, "bbox": [-15.0, -3.0, 700.7, 500.2], "candidate_id": None,
         "candidate_score": None},
    ])
    body = client.post("/api/v1/dev/recognize", headers=admin_headers, json={"image": MINIMAL_PNG}).json()
    assert seen["include_bbox"] is True
    assert body["image_width"] == 640 and body["image_height"] == 480
    assert body["results"][0]["bbox"] == [10, 21, 110, 141]
    assert body["results"][1]["bbox"] == [0, 0, 640, 480]  # clamped to the image
    assert all(isinstance(v, int) for r in body["results"] for v in r["bbox"])
    assert [r["index"] for r in body["results"]] == [1, 2]


def test_dev_recognize_statuses(client, monkeypatch, admin_headers):
    from vista.backend.app.db import SessionLocal
    from vista.backend.app.models.student import Student
    db = SessionLocal()
    known = db.query(Student).first()
    known_id, known_name = known.student_id, known.name
    db.close()
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    _fake_faces(monkeypatch, [
        {"student_id": known_id, "confidence": 0.72, "bbox": [0, 0, 5, 5], "decided_by": "gallery"},
        {"student_id": None, "confidence": 0.41, "bbox": [0, 0, 5, 5], "candidate_id": known_id,
         "candidate_score": 0.41, "candidate_source": "gallery"},
        {"student_id": None, "confidence": 0.05, "bbox": [0, 0, 5, 5], "candidate_id": known_id,
         "candidate_score": 0.05, "candidate_source": "gallery"},
        {"student_id": None, "confidence": 0.0, "bbox": [0, 0, 5, 5], "candidate_id": None,
         "candidate_score": None},
    ])
    results = client.post("/api/v1/dev/recognize", headers=admin_headers, json={"image": MINIMAL_PNG}).json()["results"]
    assert [r["status"] for r in results] == ["recognized", "below_threshold", "unknown", "unknown"]
    assert results[0]["student_name"] == known_name
    assert results[1]["candidate_id"] == known_id
    assert results[1]["candidate_name"] == known_name
    assert results[1]["candidate_score"] == 0.41
    assert "candidate_id" not in results[0] and "candidate_id" not in results[2]


def test_dev_recognize_no_db_writes_with_bbox(client, monkeypatch, teacher_headers):
    monkeypatch.setenv("VISTA_DEV_MODE", "1")
    _fake_faces(monkeypatch, [{"student_id": None, "confidence": 0.5, "bbox": [1, 2, 3, 4],
                               "candidate_id": "X", "candidate_score": 0.5}])
    before = _counts()
    assert client.post("/api/v1/dev/recognize", headers=teacher_headers, json={"image": MINIMAL_PNG}).status_code == 200
    assert _counts() == before


@pytest.mark.parametrize("flag", [None, "1"])
def test_mark_batch_response_has_no_bbox_keys(client, monkeypatch, admin_headers, flag):
    """Normal endpoints call the vision layer without include_bbox and never expose boxes."""
    from vista.backend.app.routes import attendance
    if flag:
        monkeypatch.setenv("VISTA_DEV_MODE", flag)
    else:
        monkeypatch.delenv("VISTA_DEV_MODE", raising=False)
    kwargs_seen = []
    def spy(path, **kw):
        kwargs_seen.append(kw)
        return [{"student_id": None, "confidence": 0.3, "liveness_passed": True}]

    monkeypatch.setattr(attendance, "_call_vision_all", spy)
    res = client.post("/api/v1/attendance/mark-batch", headers=admin_headers,
                      json={"image": MINIMAL_PNG, "classroom_id": "CSE-3A", "session_date": "2030-01-03"})
    assert res.status_code == 200
    assert "bbox" not in res.text and "image_width" not in res.text
    assert set(res.json()) >= {"faces_detected", "results"}
    assert kwargs_seen, "vision was never called"
    assert all("include_bbox" not in kw for kw in kwargs_seen)


def test_recognize_all_default_results_have_no_bbox(monkeypatch):
    import importlib
    rec = importlib.import_module("vista.vision.recognize")

    class Det:
        def detect(self, p):
            return [{"bbox": [1.0, 2.0, 30.0, 40.0]}]

    monkeypatch.setattr(rec, "get_detector", lambda: Det())
    monkeypatch.setattr(rec, "_classify_detected_face", lambda p, f, with_candidate=False: {
        "student_id": None, "confidence": 0.4, "candidate_id": "X1", "candidate_score": 0.4, "candidate_source": "gallery"})
    plain = rec.recognize_all("x.jpg", skip_liveness=True)[0]
    assert set(plain) == {"student_id", "confidence", "liveness_passed", "decided_by"}
    boxed = rec.recognize_all("x.jpg", skip_liveness=True, include_bbox=True)[0]
    assert boxed["bbox"] == [1.0, 2.0, 30.0, 40.0] and boxed["candidate_id"] == "X1"


def test_best_rejected_candidate_does_not_change_acceptance(monkeypatch):
    import importlib
    rec = importlib.import_module("vista.vision.recognize")
    monkeypatch.setattr(rec, "_match_student_gallery", lambda f: {
        "student_id": None, "confidence": 0.41, "matched": False, "candidate_id": "G1"})
    monkeypatch.setattr(rec, "_crop_face", lambda p, b: object())
    monkeypatch.setattr(rec, "classify_face", lambda crop, with_candidate=False: (
        {"student_id": None, "confidence": 0.30, "candidate_id": "C1"} if with_candidate
        else {"student_id": None, "confidence": 0.30}))
    plain = rec._classify_detected_face("x.jpg", {"bbox": [0, 0, 1, 1]})
    with_c = rec._classify_detected_face("x.jpg", {"bbox": [0, 0, 1, 1]}, with_candidate=True)
    assert plain == {"student_id": None, "confidence": 0.41}
    assert with_c["student_id"] is None and with_c["confidence"] == 0.41
    assert with_c["candidate_id"] == "G1" and with_c["candidate_source"] == "gallery"