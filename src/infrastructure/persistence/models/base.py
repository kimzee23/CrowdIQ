"""
CrowdIQ — SQLAlchemy Declarative Base
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# Reusable timezone-aware DateTime column type.
# Maps to TIMESTAMP WITH TIME ZONE in PostgreSQL.
TzDateTime = DateTime(timezone=True)


class Base(DeclarativeBase):
    pass
