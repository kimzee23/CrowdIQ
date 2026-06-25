"""
CrowdIQ — Prediction Domain Entities
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


def _now() -> datetime:
    return datetime.now()


class PredictionStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    LOCKED = "locked"
    AWAITING_RESOLUTION = "awaiting_resolution"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class PredictionType(str, Enum):
    BINARY = "binary"
    MULTIPLE_CHOICE = "multiple_choice"
    PROBABILITY = "probability"
    TIMED = "timed"


@dataclass
class PredictionOption:
    id: str
    prediction_id: str
    option_text: str
    vote_count: int = 0


@dataclass
class Category:
    id: str
    name: str
    slug: str
    created_at: datetime = field(default_factory=_now)


@dataclass
class Prediction:
    id: str
    creator_id: str
    title: str
    description: str
    category_id: str
    prediction_type: PredictionType
    status: PredictionStatus = PredictionStatus.DRAFT
    options: List[PredictionOption] = field(default_factory=list)
    close_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolved_option_id: Optional[str] = None
    view_count: int = 0
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    # ── Business rules ────────────────────────────────────────────────────────

    def can_vote(self) -> bool:
        return self.status == PredictionStatus.OPEN

    def can_edit(self) -> bool:
        return self.status == PredictionStatus.DRAFT

    def can_close(self) -> bool:
        return self.status == PredictionStatus.OPEN

    def can_resolve(self) -> bool:
        return self.status in (
            PredictionStatus.LOCKED,
            PredictionStatus.AWAITING_RESOLUTION,
        )

    def total_votes(self) -> int:
        return sum(o.vote_count for o in self.options)
