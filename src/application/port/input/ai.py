"""
CrowdIQ — AI Module DTOs
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    prediction_id: str
    text: str = Field(..., min_length=10)


class FactCheckRequest(BaseModel):
    claim: str = Field(..., min_length=5)


class ProbabilityRequest(BaseModel):
    prediction_id: str
    context: str = Field(default="")


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=5)


class TrendAnalysisRequest(BaseModel):
    topic: str = Field(..., min_length=3)


class AIResponse(BaseModel):
    result: str
    confidence: float | None = None
    sentiment: str | None = None
    metadata: dict | None = None
