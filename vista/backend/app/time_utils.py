"""
Time Utilities for VISTA
========================
Strict Server-Side Time Management in Asia/Kolkata (IST = UTC+5:30).
All persistent timestamps are stored in UTC ISO 8601 strings.
All period/schedule calculations resolve in Asia/Kolkata.

Supports DEV-ONLY clock mocking via VISTA_FAKE_NOW (ignored in production).
"""
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import Any

# Asia/Kolkata timezone offset is fixed at +05:30
IST_OFFSET = timezone(timedelta(hours=5, minutes=30))


def get_current_ist_datetime() -> datetime:
    """
    Returns current datetime in Asia/Kolkata timezone.
    If VISTA_ENV is 'development' (or 'testing') and VISTA_FAKE_NOW is set,
    uses the mocked timestamp.
    """
    env = os.getenv("VISTA_ENV", "development").lower()
    fake_now = os.getenv("VISTA_FAKE_NOW")
    if env in ("development", "testing") and fake_now:
        try:
            dt = datetime.fromisoformat(fake_now)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=IST_OFFSET)
            else:
                dt = dt.astimezone(IST_OFFSET)
            return dt
        except Exception:
            pass

    return datetime.now(timezone.utc).astimezone(IST_OFFSET)


def get_current_utc_iso() -> str:
    """Returns current UTC ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def get_ist_day_of_week(dt: datetime | None = None) -> int:
    """
    Returns weekday integer where 0=Monday, 1=Tuesday ... 5=Saturday, 6=Sunday.
    """
    if dt is None:
        dt = get_current_ist_datetime()
    return dt.weekday()


def get_ist_time_str(dt: datetime | None = None) -> str:
    """Returns 'HH:MM' string in IST."""
    if dt is None:
        dt = get_current_ist_datetime()
    return dt.strftime("%H:%M")


def get_ist_date_str(dt: datetime | None = None) -> str:
    """Returns 'YYYY-MM-DD' in IST."""
    if dt is None:
        dt = get_current_ist_datetime()
    return dt.strftime("%Y-%m-%d")


def time_to_minutes(time_str: str) -> int:
    """Converts 'HH:MM' to minutes from midnight."""
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def resolve_slot_status(start_time: str, end_time: str, target_time_str: str, grace_minutes: int = 10) -> str:
    """
    Determines status of a slot relative to target time:
    - 'now': target time is within [start_time, end_time] OR within grace window when no other period active.
    - 'upcoming': target time is before start_time.
    - 'past': target time is after end_time.
    """
    target_m = time_to_minutes(target_time_str)
    start_m = time_to_minutes(start_time)
    end_m = time_to_minutes(end_time)

    if start_m <= target_m <= end_m:
        return "now"
    elif target_m < start_m:
        if (start_m - target_m) <= grace_minutes:
            return "grace_upcoming"  # Within pre-period grace
        return "upcoming"
    else:
        if (target_m - end_m) <= grace_minutes:
            return "grace_post"  # Within post-period grace
        return "past"
