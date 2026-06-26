"""
Monitoring & Observability
===========================
1. Structured JSON logging with request IDs
2. Prometheus-compatible metrics
3. Error aggregation
4. System health metrics
5. Alert system (webhook notifications)

Metrics endpoint: GET /metrics
"""
from __future__ import annotations

import json
import logging
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import httpx

# ═══════════════════════════════════════════════════════════════
# 1. STRUCTURED JSON LOGGING
# ═══════════════════════════════════════════════════════════════

class JSONFormatter(logging.Formatter):
    """Outputs log records as JSON for machine parsing."""
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        # Add extra fields if present
        for key in ("request_id", "user_id", "method", "path", "status", "latency_ms", "error"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)
        return json.dumps(log_entry)


def setup_logging():
    """Configure structured JSON logging for production."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
    # Suppress noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


# ═══════════════════════════════════════════════════════════════
# 2. PROMETHEUS-COMPATIBLE METRICS
# ═══════════════════════════════════════════════════════════════

class Metrics:
    """In-memory metrics collector (Prometheus-compatible output)."""

    def __init__(self):
        self.request_count = 0
        self.request_errors = 0
        self.request_latencies: list[float] = []  # Last 1000 latencies
        self.status_counts: dict[int, int] = defaultdict(int)
        self.endpoint_counts: dict[str, int] = defaultdict(int)
        self.active_connections = 0
        self.start_time = time.time()

        # Error tracking
        self.errors: list[dict] = []  # Last 50 errors
        self.error_count_by_type: dict[str, int] = defaultdict(int)

    def record_request(self, method: str, path: str, status: int, latency_ms: float):
        self.request_count += 1
        self.status_counts[status] += 1
        self.endpoint_counts[f"{method} {path}"] += 1
        self.request_latencies.append(latency_ms)
        if len(self.request_latencies) > 1000:
            self.request_latencies = self.request_latencies[-1000:]
        if status >= 400:
            self.request_errors += 1

    def record_error(self, error_type: str, message: str, path: str = ""):
        self.error_count_by_type[error_type] += 1
        self.errors.append({
            "type": error_type,
            "message": message[:200],
            "path": path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if len(self.errors) > 50:
            self.errors = self.errors[-50:]

    def get_percentile(self, p: float) -> float:
        if not self.request_latencies:
            return 0.0
        sorted_lat = sorted(self.request_latencies)
        idx = int(len(sorted_lat) * p / 100)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]

    def to_prometheus(self) -> str:
        """Output metrics in Prometheus text format."""
        uptime = time.time() - self.start_time
        lines = [
            f"# HELP vista_requests_total Total HTTP requests",
            f"# TYPE vista_requests_total counter",
            f"vista_requests_total {self.request_count}",
            f"",
            f"# HELP vista_errors_total Total HTTP errors (4xx+5xx)",
            f"# TYPE vista_errors_total counter",
            f"vista_errors_total {self.request_errors}",
            f"",
            f"# HELP vista_uptime_seconds Server uptime",
            f"# TYPE vista_uptime_seconds gauge",
            f"vista_uptime_seconds {uptime:.0f}",
            f"",
            f"# HELP vista_latency_p50_ms 50th percentile latency",
            f"# TYPE vista_latency_p50_ms gauge",
            f"vista_latency_p50_ms {self.get_percentile(50):.1f}",
            f"",
            f"# HELP vista_latency_p95_ms 95th percentile latency",
            f"# TYPE vista_latency_p95_ms gauge",
            f"vista_latency_p95_ms {self.get_percentile(95):.1f}",
            f"",
            f"# HELP vista_latency_p99_ms 99th percentile latency",
            f"# TYPE vista_latency_p99_ms gauge",
            f"vista_latency_p99_ms {self.get_percentile(99):.1f}",
            f"",
        ]
        # Status code breakdown
        for status, count in sorted(self.status_counts.items()):
            lines.append(f'vista_status_code{{code="{status}"}} {count}')

        return "\n".join(lines)

    def to_json(self) -> dict:
        """Output metrics as JSON (for dashboard)."""
        uptime = time.time() - self.start_time
        return {
            "uptime_seconds": round(uptime),
            "total_requests": self.request_count,
            "total_errors": self.request_errors,
            "error_rate_pct": round(self.request_errors / max(self.request_count, 1) * 100, 2),
            "latency_p50_ms": round(self.get_percentile(50), 1),
            "latency_p95_ms": round(self.get_percentile(95), 1),
            "latency_p99_ms": round(self.get_percentile(99), 1),
            "status_codes": dict(self.status_counts),
            "top_endpoints": dict(sorted(self.endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "recent_errors": self.errors[-10:],
            "error_types": dict(self.error_count_by_type),
        }


# Global metrics instance
metrics = Metrics()


# ═══════════════════════════════════════════════════════════════
# 3. ALERT SYSTEM (Webhook Notifications)
# ═══════════════════════════════════════════════════════════════

ALERT_WEBHOOK_URL = os.getenv("VISTA_ALERT_WEBHOOK", "")
# Supports: Slack webhook, Discord webhook, or any HTTP POST endpoint

_last_alert_time: dict[str, float] = {}
ALERT_COOLDOWN = 300  # 5 min between same alert type


def send_alert(alert_type: str, message: str, severity: str = "warning", details: dict | None = None):
    """
    Send an alert via webhook. Deduplicates within cooldown period.

    alert_type: "high_risk_student" | "system_error" | "enrollment_failed" | "auth_brute_force"
    severity: "info" | "warning" | "critical"
    """
    now = time.time()

    # Cooldown check — don't spam same alert
    if alert_type in _last_alert_time:
        if now - _last_alert_time[alert_type] < ALERT_COOLDOWN:
            return
    _last_alert_time[alert_type] = now

    # Log the alert
    logger = logging.getLogger("vista.alerts")
    logger.warning(f"ALERT [{severity}] {alert_type}: {message}")

    # Send webhook if configured
    if not ALERT_WEBHOOK_URL:
        return

    payload = {
        "text": f"🚨 *VISTA Alert* [{severity.upper()}]\n*{alert_type}*: {message}",
        "alert_type": alert_type,
        "severity": severity,
        "message": message,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        # Fire and forget (non-blocking)
        import threading
        def _send():
            try:
                httpx.post(ALERT_WEBHOOK_URL, json=payload, timeout=5)
            except Exception:
                pass
        threading.Thread(target=_send, daemon=True).start()
    except Exception:
        pass


def alert_high_risk_student(student_id: str, student_name: str, risk_level: str, reasons: list[str]):
    """Trigger alert when a student is flagged HIGH risk."""
    if risk_level != "high":
        return
    send_alert(
        alert_type="high_risk_student",
        message=f"{student_name} ({student_id}) flagged HIGH risk: {reasons[0] if reasons else 'multiple factors'}",
        severity="warning",
        details={"student_id": student_id, "reasons": reasons},
    )


def alert_system_error(error_type: str, message: str):
    """Trigger alert on repeated system errors."""
    if metrics.error_count_by_type.get(error_type, 0) >= 5:
        send_alert(
            alert_type="system_error",
            message=f"Repeated error ({error_type}): {message}",
            severity="critical",
        )
