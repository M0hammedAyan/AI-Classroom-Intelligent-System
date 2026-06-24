from .auth import router as auth_router
from .attendance import router as attendance_router
from .students import router as students_router
from .risk import router as risk_router
from .export import router as export_router
from .enroll import router as enroll_router
from .lms import router as lms_router
from .admin import router as admin_router
from .mentor import router as mentor_router
from .dashboards import router as dashboards_router

__all__ = ["auth_router", "attendance_router", "students_router", "risk_router", "export_router", "enroll_router", "lms_router", "admin_router", "mentor_router", "dashboards_router"]
