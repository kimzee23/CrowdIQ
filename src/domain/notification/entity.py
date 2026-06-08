"""
CrowdIQ — Notification Domain Entity
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


class NotificationType(str, Enum):
    PREDICTION_CLOSED = "prediction_closed"
    PREDICTION_RESOLVED = "prediction_resolved"
    NEW_FOLLOWER = "new_follower"
    MENTION = "mention"
    COMMENT = "comment"
    VOTE = "vote"
    STAKE_RESULT = "stake_result"
    SYSTEM = "system"


@dataclass
class Notification:
    id: str
    user_id: str
    type: NotificationType
    message: str
    is_read: bool = False
    reference_id: Optional[str] = None  # prediction_id, user_id, …
    created_at: datetime = field(default_factory=_now)
