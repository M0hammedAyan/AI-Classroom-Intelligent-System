from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import create_tables, seed_demo_data, SessionLocal
from .routes import auth, attendance, students, risk, export, enroll, lms, admin, mentor, dashboards, student_portal, notifications, reports, academics
from .websocket import ws_manager

app = FastAPI(title="VISTA API", version="1.0.0")

# ── Monitoring setup ──
from .monitoring import setup_logging, metrics, Metrics
setup_logging()

# ── Request logging + metrics middleware ──
import time as _time
import uuid as _uuid
import logging
_logger = logging.getLogger("vista.requests")

@app.middleware("http")
async def observe_requests(request, call_next):
    request_id = str(_uuid.uuid4())[:8]
    start = _time.time()
    response = await call_next(request)
    duration = round((_time.time() - start) * 1000, 1)

    # Record metrics
    metrics.record_request(request.method, request.url.path, response.status_code, duration)

    # Structured log
    _logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)",
        extra={"request_id": request_id, "method": request.method, "path": request.url.path, "status": response.status_code, "latency_ms": duration},
    )

    # Track errors
    if response.status_code >= 500:
        metrics.record_error("server_error", f"{request.method} {request.url.path}", request.url.path)

    # Add request ID to response
    response.headers["X-Request-ID"] = request_id
    return response


# ── Secure headers middleware ──
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
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
app.include_router(mentor.router)
app.include_router(dashboards.router)
app.include_router(student_portal.router)
app.include_router(notifications.router)
app.include_router(reports.router)
app.include_router(academics.router)


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
    """Health check with DB connectivity + system metrics."""
    from sqlalchemy import text as sa_text
    import psutil
    try:
        db = SessionLocal()
        db.execute(sa_text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    try:
        memory = psutil.virtual_memory()
        mem_pct = memory.percent
    except Exception:
        mem_pct = None

    return {
        "status": "ok",
        "database": db_status,
        "memory_pct": mem_pct,
        "uptime_seconds": round(_time.time() - metrics.start_time),
        "total_requests": metrics.request_count,
    }


@app.get("/metrics")
def prometheus_metrics():
    """Prometheus-compatible metrics endpoint."""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(metrics.to_prometheus(), media_type="text/plain")


@app.get("/metrics/json")
def json_metrics():
    """JSON metrics for internal dashboard."""
    return metrics.to_json()


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
