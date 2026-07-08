"""
CrowdIQ — Prediction & Category DTOs
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.domain.model.prediction import PredictionStatus, PredictionType


class PredictionOptionRequest(BaseModel):
    option_text: str = Field(..., min_length=1, max_length=500)


class CreatePredictionRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)
    category_id: str
    prediction_type: PredictionType
    options: List[PredictionOptionRequest] = Field(default_factory=list)
    close_at: Optional[datetime] = None


class UpdatePredictionRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = None
    category_id: Optional[str] = None
    close_at: Optional[datetime] = None


class ResolvePredictionRequest(BaseModel):
    winning_option_id: str


class PredictionOptionResponse(BaseModel):
    id: str
    prediction_id: str
    option_text: str
    vote_count: int


class PredictionResponse(BaseModel):
    id: str
    creator_id: str
    title: str
    description: str
    category_id: str
    prediction_type: str
    status: str
    options: List[PredictionOptionResponse]
    close_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolved_option_id: Optional[str]
    view_count: int
    total_votes: int
    created_at: datetime
    updated_at: datetime


class PredictionListResponse(BaseModel):
    predictions: List[PredictionResponse]
    total: int
    skip: int
    limit: int


# ── Category ──────────────────────────────────────────────────────────────────

class CreateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class UpdateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
