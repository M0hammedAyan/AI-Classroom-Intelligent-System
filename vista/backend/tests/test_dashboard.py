"""Tests for role-scoped dashboard endpoints."""


def test_admin_dashboard(client, admin_headers):
    res = client.get("/api/v1/dashboard/admin", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "students" in data
    assert "high_risk" in data
    assert "teachers" in data


def test_admin_dashboard_teacher_forbidden(client, teacher_headers):
    res = client.get("/api/v1/dashboard/admin", headers=teacher_headers)
    assert res.status_code == 403


def test_teacher_dashboard(client, teacher_headers):
    res = client.get("/api/v1/dashboard/teacher", headers=teacher_headers)
    assert res.status_code == 200
    data = res.json()
    assert "my_subjects" in data
    assert "my_classes" in data


def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
