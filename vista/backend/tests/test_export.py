"""Tests for export endpoints."""


def test_export_csv(client, admin_headers):
    res = client.get("/api/v1/export/report?classroom_id=CSE-3A&from_date=2026-04-01&to_date=2026-06-24&format=csv", headers=admin_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment" in res.headers.get("content-disposition", "")


def test_export_pdf(client, admin_headers):
    res = client.get("/api/v1/export/report?classroom_id=CSE-3A&from_date=2026-04-01&to_date=2026-06-24&format=pdf", headers=admin_headers)
    assert res.status_code == 200
    assert "application/pdf" in res.headers["content-type"]


def test_export_invalid_date_range(client, admin_headers):
    res = client.get("/api/v1/export/report?classroom_id=CSE-3A&from_date=2026-06-24&to_date=2026-01-01&format=csv", headers=admin_headers)
    assert res.status_code == 400
    assert res.json()["detail"]["code"] == "INVALID_DATE_RANGE"
