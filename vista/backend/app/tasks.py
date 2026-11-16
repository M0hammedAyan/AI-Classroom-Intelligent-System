"""
Async Processing Layer
======================
Zero-dependency async task processing using Python's concurrent.futures ThreadPool.
Provides background tasks for:
- Face recognition
- Batch risk recomputation
- PDF report generation
"""
from __future__ import annotations

import concurrent.futures
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def run_async(func: Callable, *args: Any, **kwargs: Any) -> concurrent.futures.Future:
    """Submit a function to run asynchronously on the thread pool."""
    return _executor.submit(func, *args, **kwargs)
