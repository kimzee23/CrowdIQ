"""
CrowdIQ — Reputation & Wallet Domain Entities
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _now() -> datetime:
    return datetime.now()


@dataclass
class ReputationHistory:
    id: str
    user_id: str
    points: int          # positive = gain, negative = loss
    reason: str
    created_at: datetime = field(default_factory=_now)


@dataclass
class WalletTransaction:
    id: str
    user_id: str
    amount: int          # positive = credit, negative = debit
    reason: str
    prediction_id: Optional[str] = None
    created_at: datetime = field(default_factory=_now)
