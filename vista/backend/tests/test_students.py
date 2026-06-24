"""Tests for student endpoints."""


def test_list_students(client, admin_headers):
    res = client.get("/api/v1/students", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "students" in data
    assert "total" in data
    assert data["total"] >= 1


def test_list_students_pagination(client, admin_headers):
    res = client.get("/api/v1/students?page=1&page_size=2", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_get_student_exists(client, admin_headers):
    res = client.get("/api/v1/students/CS22B001", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == "CS22B001"
    assert "name" in data


def test_get_student_not_found(client, admin_headers):
    res = client.get("/api/v1/students/NONEXISTENT", headers=admin_headers)
    assert res.status_code == 404
    assert res.json()["detail"]["code"] == "STUDENT_NOT_FOUND"
