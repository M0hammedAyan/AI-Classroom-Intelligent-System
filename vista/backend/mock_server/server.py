"""
VISTA Mock Server
=================
Returns correctly-shaped fixture data for all API contract endpoints.
Frontend (Member 3) uses this while the real backend is being built.

Run from project root:
    uvicorn vista.backend.mock_server.server:app --port 8001 --reload

All endpoints match the shape in docs/API_CONTRACT.md exactly.
Token validation is bypassed — any non-empty Bearer token is accepted.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import csv
import io

app = FastAPI(title="VISTA Mock Server", version="1.0.0-mock")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Auth bypass helper
# ---------------------------------------------------------------------------

def _require_token(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": "MISSING_TOKEN", "message": "Authorization header required."})


# ---------------------------------------------------------------------------
# Fixture data
# ---------------------------------------------------------------------------

MOCK_TOKEN = "mock.jwt.token"

MOCK_STUDENTS = [
    {"student_id": "CS22B001", "name": "Aarav Shah",   "class": "CSE-3A", "enrolled_at": "2022-08-01", "is_active": True},
    {"student_id": "CS22B002", "name": "Priya Nair",   "class": "CSE-3A", "enrolled_at": "2022-08-01", "is_active": True},
    {"student_id": "CS22B003", "name": "Rohan Mehta",  "class": "CSE-3A", "enrolled_at": "2022-08-01", "is_active": True},
    {"student_id": "CS22B004", "name": "Sneha Rao",    "class": "CSE-3A", "enrolled_at": "2022-08-01", "is_active": True},
    {"student_id": "CS22B005", "name": "Vikram Patel", "class": "CSE-3A", "enrolled_at": "2022-08-01", "is_active": True},
]

MOCK_ATTENDANCE = [
    {"attendance_id": "att-001", "student_id": "CS22B001", "student_name": "Aarav Shah",   "status": "present",          "confidence": 0.97, "marked_at": "2026-06-20T09:05:00Z", "is_manual_override": False},
    {"attendance_id": "att-002", "student_id": "CS22B002", "student_name": "Priya Nair",   "status": "present",          "confidence": 0.94, "marked_at": "2026-06-20T09:06:00Z", "is_manual_override": False},
    {"attendance_id": None,      "student_id": "CS22B003", "student_name": "Rohan Mehta",  "status": "absent",           "confidence": None, "marked_at": None,                  "is_manual_override": False},
    {"attendance_id": "att-003", "student_id": "CS22B004", "student_name": "Sneha Rao",    "status": "liveness_failed",  "confidence": 0.61, "marked_at": "2026-06-20T09:08:00Z", "is_manual_override": False},
    {"attendance_id": "att-004", "student_id": "CS22B005", "student_name": "Vikram Patel", "status": "present",          "confidence": 0.91, "marked_at": "2026-06-20T09:09:00Z", "is_manual_override": False},
]

MOCK_RISK = [
    {"student_id": "CS22B001", "student_name": "Aarav Shah",   "risk_level": "low",    "reasons": [],                                                                          "confidence": "high",     "computed_at": "2026-06-20T08:00:00Z"},
    {"student_id": "CS22B002", "student_name": "Priya Nair",   "risk_level": "medium", "reasons": ["Attendance dropped 15% recently", "Average internal marks at 58%"],        "confidence": "moderate", "computed_at": "2026-06-20T08:00:00Z"},
    {"student_id": "CS22B003", "student_name": "Rohan Mehta",  "risk_level": "high",   "reasons": ["Attendance at 45% — below 75% threshold", "3 consecutive absences"],       "confidence": "high",     "computed_at": "2026-06-20T08:00:00Z"},
    {"student_id": "CS22B004", "student_name": "Sneha Rao",    "risk_level": "low",    "reasons": [],                                                                          "confidence": "high",     "computed_at": "2026-06-20T08:00:00Z"},
    {"student_id": "CS22B005", "student_name": "Vikram Patel", "risk_level": "medium", "reasons": ["Marks declined 22% from recent peak", "Declining score trend"],            "confidence": "moderate", "computed_at": "2026-06-20T08:00:00Z"},
]

_RISK_BY_ID = {r["student_id"]: r for r in MOCK_RISK}
_STUDENT_BY_ID = {s["student_id"]: s for s in MOCK_STUDENTS}

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/v1/auth/login")
def login(body: LoginRequest):
    valid = {
        "admin@vista.local": ("admin123", "admin", "Admin User"),
        "teacher@vista.local": ("teacher123", "teacher", "Demo Teacher"),
    }
    if body.email not in valid or valid[body.email][0] != body.password:
        raise HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."})
    _role, _name = valid[body.email][1], valid[body.email][2]
    return {"token": MOCK_TOKEN, "role": _role, "user_id": "mock-user-id", "name": _name}

@app.post("/api/v1/auth/logout")
def logout(authorization: str = Header(default="")):
    _require_token(authorization)
    return {"message": "Logged out."}

# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------

@app.get("/api/v1/students")
def list_students(page: int = 1, page_size: int = 50, authorization: str = Header(default="")):
    _require_token(authorization)
    return {"students": MOCK_STUDENTS, "total": len(MOCK_STUDENTS), "page": page, "page_size": page_size}

@app.get("/api/v1/students/{student_id}")
def get_student(student_id: str, authorization: str = Header(default="")):
    _require_token(authorization)
    s = _STUDENT_BY_ID.get(student_id)
    if not s:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id}."})
    return s

# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------

class MarkRequest(BaseModel):
    image: str
    classroom_id: str
    session_date: str

@app.post("/api/v1/attendance/mark")
def mark_attendance(body: MarkRequest, authorization: str = Header(default="")):
    _require_token(authorization)
    now = datetime.now(timezone.utc).isoformat()
    return {
        "student_id": "CS22B001",
        "student_name": "Aarav Shah",
        "status": "present",
        "confidence": 0.96,
        "liveness_passed": True,
        "attendance_id": "mock-att-999",
        "marked_at": now,
    }

@app.get("/api/v1/attendance/log")
def attendance_log(classroom_id: str, date: str, authorization: str = Header(default="")):
    _require_token(authorization)
    return {"classroom_id": classroom_id, "date": date, "records": MOCK_ATTENDANCE, "total": len(MOCK_ATTENDANCE)}

class PatchRequest(BaseModel):
    status: str
    note: str | None = None

@app.patch("/api/v1/attendance/{attendance_id}")
def patch_attendance(attendance_id: str, body: PatchRequest, authorization: str = Header(default="")):
    _require_token(authorization)
    if body.status not in {"present", "absent"}:
        raise HTTPException(status_code=400, detail={"code": "INVALID_STATUS", "message": "status must be 'present' or 'absent'."})
    return {
        "attendance_id": attendance_id,
        "student_id": "CS22B001",
        "student_name": "Aarav Shah",
        "status": body.status,
        "confidence": None,
        "marked_at": datetime.now(timezone.utc).isoformat(),
        "is_manual_override": True,
    }

# ---------------------------------------------------------------------------
# Risk
# ---------------------------------------------------------------------------

@app.get("/api/v1/students/{student_id}/risk")
def get_student_risk(student_id: str, authorization: str = Header(default="")):
    _require_token(authorization)
    if student_id not in _STUDENT_BY_ID:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id}."})
    flag = _RISK_BY_ID.get(student_id)
    if not flag:
        raise HTTPException(status_code=404, detail={"code": "RISK_NOT_COMPUTED", "message": "Risk not yet computed."})
    return flag

@app.get("/api/v1/risk")
def list_risk(risk_level: str | None = None, page: int = 1, page_size: int = 50, authorization: str = Header(default="")):
    _require_token(authorization)
    flags = MOCK_RISK if not risk_level else [r for r in MOCK_RISK if r["risk_level"] == risk_level.lower()]
    return {"flags": flags, "total": len(flags), "page": page, "page_size": page_size}

@app.post("/api/v1/students/{student_id}/risk/recompute")
def recompute_risk(student_id: str, authorization: str = Header(default="")):
    _require_token(authorization)
    if student_id not in _STUDENT_BY_ID:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id}."})
    return _RISK_BY_ID.get(student_id, MOCK_RISK[0])

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

@app.get("/api/v1/export/report")
def export_report(classroom_id: str, from_date: str, to_date: str, format: str = "csv", authorization: str = Header(default="")):
    _require_token(authorization)
    if from_date > to_date:
        raise HTTPException(status_code=400, detail={"code": "INVALID_DATE_RANGE", "message": "to_date must be >= from_date."})
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["student_id", "name", from_date])
    writer.writeheader()
    for s in MOCK_STUDENTS:
        writer.writerow({"student_id": s["student_id"], "name": s["name"], from_date: "present"})
    filename = f"attendance_{classroom_id}_{from_date}_{to_date}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "server": "mock"}
