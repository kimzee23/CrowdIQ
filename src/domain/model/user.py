"""
CrowdIQ — User Domain Entity
Pure Python dataclass; zero infrastructure dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, date
from enum import Enum
from typing import Optional


def _now() -> datetime:
    return datetime.now()


class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class ReputationLevel(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    LEGEND = "legend"


@dataclass
class User:
    id: str
    username: str
    email: str
    hashed_password: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: UserRole = UserRole.USER
    reputation_score: int = 0
    accuracy_score: float = 0.0
    total_predictions: int = 0
    resolved_predictions: int = 0
    virtual_points: int = 1000
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)
    cover_photo_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    social_linkedin: Optional[str] = None
    social_github: Optional[str] = None
    social_twitter: Optional[str] = None
    social_instagram: Optional[str] = None
    social_facebook: Optional[str] = None
    social_youtube: Optional[str] = None
    social_tiktok: Optional[str] = None
    social_portfolio: Optional[str] = None
    interests: list[str] = field(default_factory=list)
    hobbies: list[str] = field(default_factory=list)
    favorite_topics: list[str] = field(default_factory=list)
    preferred_language: str = "en"

    # ── Derived properties ────────────────────────────────────────────────────

    @property
    def reputation_level(self) -> ReputationLevel:
        score = self.reputation_score
        if score >= 5000:
            return ReputationLevel.LEGEND
        if score >= 1500:
            return ReputationLevel.PLATINUM
        if score >= 500:
            return ReputationLevel.GOLD
        if score >= 100:
            return ReputationLevel.SILVER
        return ReputationLevel.BRONZE

    @property
    def win_rate(self) -> float:
        if self.total_predictions == 0:
            return 0.0
        return round(self.resolved_predictions / self.total_predictions * 100, 2)

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def is_moderator_or_above(self) -> bool:
        return self.role in (UserRole.MODERATOR, UserRole.ADMIN)
