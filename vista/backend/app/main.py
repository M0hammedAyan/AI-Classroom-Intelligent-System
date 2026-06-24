from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import create_tables, seed_demo_data, SessionLocal
from .routes import auth, attendance, students, risk, export, enroll, lms, admin
from .websocket import ws_manager

app = FastAPI(title="VISTA API", version="1.0.0")

# ── Request logging middleware ──
import time as _time
import logging
_logger = logging.getLogger("vista.requests")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

@app.middleware("http")
async def log_requests(request, call_next):
    start = _time.time()
    response = await call_next(request)
    duration = round((_time.time() - start) * 1000)
    _logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(risk.router)
app.include_router(export.router)
app.include_router(enroll.router)
app.include_router(lms.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup():
    import os
    import logging
    logger = logging.getLogger("vista")

    # Warn if using default JWT secret
    if os.getenv("VISTA_JWT_SECRET") is None:
        logger.warning("⚠️  VISTA_JWT_SECRET not set — using insecure default. Set in production!")

    create_tables()
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()

    # Start scheduled tasks (if enabled)
    from .scheduler import init_scheduler
    init_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    from .scheduler import shutdown_scheduler
    shutdown_scheduler()


@app.get("/health")
def health():
    """Health check with DB connectivity test."""
    from sqlalchemy import text as sa_text
    try:
        db = SessionLocal()
        db.execute(sa_text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok", "database": db_status}


# ---------------------------------------------------------------------------
# WebSocket endpoint for real-time dashboard updates
# ---------------------------------------------------------------------------

from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    Real-time updates for the dashboard.
    Requires valid JWT token as query param: /ws/dashboard?token=xxx
    """
    # Auth check
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return
    try:
        from .routes.auth import decode_token
        decode_token(token)
    except Exception:
        await websocket.close(code=4003, reason="Invalid token")
        return

    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await ws_manager.send_personal(websocket, {"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
