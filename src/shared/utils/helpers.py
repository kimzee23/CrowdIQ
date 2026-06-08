"""
CrowdIQ — General Utility Helpers
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Return a new UUID-4 as a lowercase string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def paginate(skip: int, limit: int) -> tuple[int, int]:
    """Clamp pagination parameters and return (skip, limit)."""
    skip = max(0, skip)
    limit = max(1, min(limit, 100))
    return skip, limit
