"""
Gunicorn Configuration — Production Multi-Worker Setup
=======================================================
Start with:
    gunicorn vista.backend.app.main:app -c vista/gunicorn.conf.py

Workers = 2 * CPU cores + 1 (standard formula)
Uses uvicorn workers for async support.
"""
import multiprocessing
import os

# Bind
bind = os.getenv("VISTA_BIND", "0.0.0.0:8000")

# Workers
workers = int(os.getenv("VISTA_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts
timeout = 120        # Kill worker if request takes >120s (face recognition can be slow)
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"      # stdout
errorlog = "-"       # stderr
loglevel = os.getenv("VISTA_LOG_LEVEL", "info")

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "vista-api"

# Preload app (shares model memory across workers)
preload_app = True

# Restart workers after N requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50
