"""
In-Memory Cache Layer
=====================
Zero-dependency, thread-safe in-memory cache with TTL support.
Provides caching for:
- Face gallery embeddings (avoid DB hits on every recognition)
- Rate limiting state
- Token blocklist
- API response caching
"""
from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)

_cache_lock = threading.Lock()
_store: dict[str, tuple[Any, float]] = {}  # key -> (value, expires_at)
_blocklist_set: set[str] = set()


def cache_get(key: str) -> str | None:
    """Get a value from cache if not expired."""
    now = time.time()
    with _cache_lock:
        if key in _store:
            val, expires_at = _store[key]
            if expires_at > now:
                return val
            _store.pop(key, None)
    return None


def cache_set(key: str, value: str, ttl: int = 60) -> None:
    """Set a value in cache with TTL (seconds)."""
    expires_at = time.time() + ttl
    with _cache_lock:
        _store[key] = (value, expires_at)


def cache_delete(key: str) -> None:
    """Delete a key from cache."""
    with _cache_lock:
        _store.pop(key, None)


def cache_gallery(gallery: dict[str, list[float]]) -> None:
    """Cache the face gallery embeddings."""
    cache_set("vista:gallery", json.dumps(gallery), ttl=120)


def get_cached_gallery() -> dict[str, list[float]] | None:
    """Get cached gallery. Returns None if not cached."""
    data = cache_get("vista:gallery")
    if data:
        return json.loads(data)
    return None


def is_token_blocklisted(token: str) -> bool:
    """Check if a token is in the blocklist."""
    with _cache_lock:
        return token in _blocklist_set


def blocklist_token(token: str, ttl: int = 8 * 3600) -> None:
    """Add token to blocklist."""
    with _cache_lock:
        _blocklist_set.add(token)
