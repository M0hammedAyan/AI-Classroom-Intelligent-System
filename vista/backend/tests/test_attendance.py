"""Tests for attendance endpoints."""


def test_attendance_log(client, admin_headers):
    res = client.get("/api/v1/attendance/log?classroom_id=CSE-3A&date=2026-05-15", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "records" in data
    assert "total" in data
    assert data["classroom_id"] == "CSE-3A"


def test_attendance_stats(client, admin_headers):
    res = client.get("/api/v1/attendance/stats?classroom_id=CSE-3A", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_sessions" in data
    assert "overall_attendance_pct" in data
    assert "weekly_summary" in data
    assert "student_summary" in data


def test_attendance_mark_invalid_image(client, admin_headers):
    res = client.post("/api/v1/attendance/mark", headers=admin_headers, json={
        "image": "not-valid-base64!!!",
        "classroom_id": "CSE-3A",
        "session_date": "2026-06-24",
    })
    assert res.status_code == 400


def test_attendance_override_not_found(client, admin_headers):
    res = client.patch("/api/v1/attendance/nonexistent-id", headers=admin_headers, json={"status": "present"})
    assert res.status_code == 404


def test_attendance_override_invalid_status(client, admin_headers):
    res = client.patch("/api/v1/attendance/some-id", headers=admin_headers, json={"status": "invalid"})
    assert res.status_code == 400
