"""
CrowdIQ — User DTOs
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    role: str
    reputation_score: int
    accuracy_score: float
    total_predictions: int
    resolved_predictions: int
    virtual_points: int
    reputation_level: str
    win_rate: float
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPublicResponse(BaseModel):
    """Reduced profile — safe to return to anyone."""
    id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    reputation_score: int
    reputation_level: str
    total_predictions: int
    win_rate: float
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=500)


class LeaderboardResponse(BaseModel):
    users: list[UserPublicResponse]
    total: int


class FollowersResponse(BaseModel):
    users: list[UserPublicResponse]
    total: int
