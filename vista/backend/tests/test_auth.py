"""Tests for authentication endpoints."""


def test_login_success(client):
    res = client.post("/api/v1/auth/login", json={"email": "admin@vista.local", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["role"] == "admin"
    assert data["name"] == "Admin User"


def test_login_wrong_password(client):
    res = client.post("/api/v1/auth/login", json={"email": "admin@vista.local", "password": "wrong"})
    assert res.status_code == 401
    assert res.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_user(client):
    res = client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "x"})
    assert res.status_code == 401


def test_protected_route_no_token(client):
    res = client.get("/api/v1/students")
    assert res.status_code == 401


def test_protected_route_invalid_token(client):
    res = client.get("/api/v1/students", headers={"Authorization": "Bearer invalid.token.here"})
    assert res.status_code == 401


def test_logout(client):
    # Get a dedicated token for this test (not shared)
    from vista.backend.app.routes.auth import _login_attempts, _blocklist
    _login_attempts.clear()
    _blocklist.clear()
    res = client.post("/api/v1/auth/login", json={"email": "admin@vista.local", "password": "admin123"})
    token = res.json()["token"]
    res = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    # Token should be revoked now
    res2 = client.get("/api/v1/students", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 401


def test_get_me(client, admin_headers):
    res = client.get("/api/v1/auth/me", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "admin"
    assert "permissions" in data
