"""Tests for risk endpoints."""


def test_list_risk_flags(client, admin_headers):
    res = client.get("/api/v1/risk", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "flags" in data
    assert "total" in data


def test_list_risk_filter_by_level(client, admin_headers):
    res = client.get("/api/v1/risk?risk_level=high", headers=admin_headers)
    assert res.status_code == 200
    for flag in res.json()["flags"]:
        assert flag["risk_level"] == "high"


def test_get_student_risk(client, admin_headers):
    # CS22B003 has high risk in seed data
    res = client.get("/api/v1/students/CS22B003/risk", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == "CS22B003"
    assert data["risk_level"] in ("low", "medium", "high")
    assert "reasons" in data


def test_get_risk_student_not_found(client, admin_headers):
    res = client.get("/api/v1/students/NONEXISTENT/risk", headers=admin_headers)
    assert res.status_code == 404


def test_recompute_risk(client, admin_headers):
    res = client.post("/api/v1/students/CS22B001/risk/recompute", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == "CS22B001"
    assert data["risk_level"] in ("low", "medium", "high")


def test_recompute_risk_teacher_forbidden(client, teacher_headers):
    res = client.post("/api/v1/students/CS22B001/risk/recompute", headers=teacher_headers)
    assert res.status_code == 403


def test_recompute_all(client, admin_headers):
    res = client.post("/api/v1/risk/recompute-all", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "recomputed" in data
    assert data["recomputed"] >= 1


def test_explain_risk(client, admin_headers):
    res = client.get("/api/v1/students/CS22B003/risk/explain", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "risk_level" in data
    assert "explainability" in data
