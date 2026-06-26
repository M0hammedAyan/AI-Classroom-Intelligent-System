"""
Redis Cache Layer
==================
Provides caching for:
- Face gallery embeddings (avoid DB hits on every recognition)
- Rate limiting state (shared across workers)
- Token blocklist (shared across workers)
- API response caching

Falls back to in-memory dict if Redis is unavailable.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("VISTA_REDIS_URL", "redis://localhost:6379/0")

_redis_client = None
_fallback_cache: dict[str, Any] = {}


def get_redis():
    """Get or create Redis connection. Returns None if unavailable."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2)
        _redis_client.ping()
        logger.info("Redis connected.")
        return _redis_client
    except Exception:
        logger.warning("Redis unavailable — using in-memory fallback cache.")
        return None


def cache_get(key: str) -> str | None:
    """Get a value from cache."""
    r = get_redis()
    if r:
        try:
            return r.get(key)
        except Exception:
            pass
    return _fallback_cache.get(key)


def cache_set(key: str, value: str, ttl: int = 60) -> None:
    """Set a value in cache with TTL (seconds)."""
    r = get_redis()
    if r:
        try:
            r.setex(key, ttl, value)
            return
        except Exception:
            pass
    _fallback_cache[key] = value


def cache_delete(key: str) -> None:
    """Delete a key from cache."""
    r = get_redis()
    if r:
        try:
            r.delete(key)
            return
        except Exception:
            pass
    _fallback_cache.pop(key, None)


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
    r = get_redis()
    if r:
        try:
            return r.sismember("vista:blocklist", token)
        except Exception:
            pass
    return token in _fallback_cache.get("_blocklist_set", set())


def blocklist_token(token: str, ttl: int = 8 * 3600) -> None:
    """Add token to blocklist."""
    r = get_redis()
    if r:
        try:
            r.sadd("vista:blocklist", token)
            r.expire("vista:blocklist", ttl)
            return
        except Exception:
            pass
    if "_blocklist_set" not in _fallback_cache:
        _fallback_cache["_blocklist_set"] = set()
    _fallback_cache["_blocklist_set"].add(token)
