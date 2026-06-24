from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import create_tables, seed_demo_data, SessionLocal
from .routes import auth, attendance, students, risk, export, enroll, lms, admin
from .websocket import ws_manager

app = FastAPI(title="VISTA API", version="1.0.0")

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
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# WebSocket endpoint for real-time dashboard updates
# ---------------------------------------------------------------------------

from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    Real-time updates for the dashboard.
    Clients receive events when:
    - Attendance is marked
    - Risk is recomputed
    - Alerts fire for HIGH risk students
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; listen for client pings
            data = await websocket.receive_text()
            if data == "ping":
                await ws_manager.send_personal(websocket, {"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
