"""
CrowdIQ — Comment DTOs
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CreateCommentRequest(BaseModel):
    prediction_id: str
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: Optional[str] = None


class UpdateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    id: str
    prediction_id: str
    user_id: str
    content: str
    parent_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
