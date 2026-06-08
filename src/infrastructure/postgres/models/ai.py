"""
CrowdIQ — AI Analysis ORM Model
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.postgres.models.base import Base, _now, _uuid


class AIAnalysisModel(Base):
    __tablename__ = "ai_analysis"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    prediction_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_now)

    prediction = relationship("PredictionModel", back_populates="ai_analysis", lazy="noload")
