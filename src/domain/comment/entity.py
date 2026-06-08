"""
CrowdIQ — Comment Domain Entity
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Comment:
    id: str
    prediction_id: str
    user_id: str
    content: str
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)
