from __future__ import annotations

import uuid
from datetime import datetime, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# In-memory token blocklist (pilot only — single process)
_blocklist: set[str] = set()


class LoginRequest(BaseModel):
    email: str
    password: str


def _make_jwt(user_id: str, role: str) -> str:
    """Minimal JWT using PyJWT — HS256, 8-hour expiry."""
    import os
    import time
    import jwt

    secret = os.getenv("VISTA_JWT_SECRET", "vista-dev-secret-change-in-prod")
    payload = {
        "sub": user_id,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + 8 * 3600,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> dict:
    import os
    import jwt

    if token in _blocklist:
        raise ValueError("Token revoked")
    secret = os.getenv("VISTA_JWT_SECRET", "vista-dev-secret-change-in-prod")
    return jwt.decode(token, secret, algorithms=["HS256"])


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": "MISSING_TOKEN", "message": "Authorization header required."})
    token = auth.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Token is invalid or expired."})
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail={"code": "ACCOUNT_DISABLED", "message": "Account is disabled."})
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Admin role required."})
    return current_user


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."})
    if not user.is_active:
        raise HTTPException(status_code=403, detail={"code": "ACCOUNT_DISABLED", "message": "Account is disabled."})
    if not bcrypt.checkpw(body.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."})

    user.last_login_at = datetime.now(timezone.utc).isoformat()
    db.commit()

    return {
        "token": _make_jwt(user.id, user.role),
        "role": user.role,
        "user_id": user.id,
        "name": user.name,
    }


@router.post("/logout")
def logout(request: Request, current_user: User = Depends(get_current_user)):
    token = request.headers["Authorization"].split(" ", 1)[1]
    _blocklist.add(token)
    return {"message": "Logged out."}
