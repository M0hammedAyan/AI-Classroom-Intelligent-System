"""Endpoint tests for attendance results returned by the personal model path."""
import base64


MINIMAL_PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n").decode()


def test_mark_attendance_accepts_personal_model_result(client, admin_headers, monkeypatch):
    from vista.backend.app.routes import attendance

    monkeypatch.setattr(
        attendance,
        "_call_vision",
        lambda _path: {
            "student_id": "1DA22AI402",
            "confidence": 0.91,
            "liveness_passed": True,
        },
    )

    response = client.post(
        "/api/v1/attendance/mark",
        headers=admin_headers,
        json={
            "image": MINIMAL_PNG,
            "classroom_id": "CSE-3A",
            "session_date": "2030-01-01",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["student_id"] == "1DA22AI402"
    assert body["status"] == "present"
    assert body["confidence"] == 0.91
    assert body["liveness_passed"] is True


def test_mark_batch_accepts_personal_model_results(client, admin_headers, monkeypatch):
    from vista.backend.app.routes import attendance

    monkeypatch.setattr(
        attendance,
        "_call_vision_all",
        lambda _path: [
            {
                "student_id": "1DA22AI402",
                "confidence": 0.88,
                "liveness_passed": True,
            },
            {
                "student_id": None,
                "confidence": 0.52,
                "liveness_passed": True,
            },
        ],
    )

    response = client.post(
        "/api/v1/attendance/mark-batch",
        headers=admin_headers,
        json={
            "image": MINIMAL_PNG,
            "classroom_id": "CSE-3A",
            "session_date": "2030-01-02",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["faces_detected"] == 2
    assert body["results"][0]["status"] == "present"
    assert body["results"][0]["confidence"] == 0.88
    assert body["results"][1]["status"] == "unrecognized"