"""
CrowdIQ — Prediction, PredictionOption & Category ORM Models
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.models.base import Base, _now, _uuid, TzDateTime


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(TzDateTime, default=_now)

    predictions = relationship("PredictionModel", back_populates="category", lazy="noload")


class PredictionModel(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    creator_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    prediction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    resolved_option_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    close_at: Mapped[Optional[datetime]] = mapped_column(TzDateTime, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(TzDateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TzDateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(TzDateTime, default=_now, onupdate=_now)

    creator = relationship("UserModel", back_populates="predictions", lazy="noload")
    category = relationship("CategoryModel", back_populates="predictions", lazy="noload")
    options = relationship(
        "PredictionOptionModel",
        back_populates="prediction",
        lazy="noload",
        cascade="all, delete-orphan",
    )
    votes = relationship("VoteModel", back_populates="prediction", lazy="noload")
    comments = relationship("CommentModel", back_populates="prediction", lazy="noload")
    ai_analysis = relationship(
        "AIAnalysisModel", back_populates="prediction", uselist=False, lazy="noload"
    )


class PredictionOptionModel(Base):
    __tablename__ = "prediction_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    prediction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    option_text: Mapped[str] = mapped_column(String(500), nullable=False)
    vote_count: Mapped[int] = mapped_column(Integer, default=0)

    prediction = relationship("PredictionModel", back_populates="options", lazy="noload")
