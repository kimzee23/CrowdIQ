"""
CrowdIQ — Vote & Stake DTOs
"""
from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class CastVoteRequest(BaseModel):
    option_id: str
    confidence: int = Field(50, ge=1, le=100)


class StakeRequest(BaseModel):
    amount: int = Field(..., ge=1)


class VoteResponse(BaseModel):
    id: str
    user_id: str
    prediction_id: str
    option_id: str
    confidence: int
    stake: int
    created_at: datetime


class VoteListResponse(BaseModel):
    votes: List[VoteResponse]
    total: int
