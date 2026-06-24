from .auth import router as auth_router
from .attendance import router as attendance_router
from .students import router as students_router
from .risk import router as risk_router
from .export import router as export_router

__all__ = ["auth_router", "attendance_router", "students_router", "risk_router", "export_router"]
