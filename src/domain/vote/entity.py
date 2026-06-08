"""
CrowdIQ — Vote Domain Entity
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Vote:
    id: str
    user_id: str
    prediction_id: str
    option_id: str
    confidence: int = 50   # 1–100 %
    stake: int = 0         # virtual points wagered
    created_at: datetime = field(default_factory=_now)
