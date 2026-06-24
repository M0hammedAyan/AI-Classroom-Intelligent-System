"""
VISTA ML Module — Academic Risk Engine
=======================================
Public API:
    calculate_risk(student_id)           — DB-backed entry point (requires backend DB)
    calculate_risk_from_metrics(metrics) — direct entry point (no DB needed)
    run_pipeline(input_data)             — XGBoost inference from flat dict
"""
from .risk_engine import (
    InsufficientDataError,
    StudentNotFoundError,
    calculate_risk,
    calculate_risk_from_metrics,
    run_pipeline,
)

__all__ = [
    "calculate_risk",
    "calculate_risk_from_metrics",
    "run_pipeline",
    "StudentNotFoundError",
    "InsufficientDataError",
]
