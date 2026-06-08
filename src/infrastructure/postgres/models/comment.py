"""
CrowdIQ — Comment ORM Model
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.postgres.models.base import Base, _now, _uuid


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    prediction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=_now)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now)

    user = relationship("UserModel", back_populates="comments", lazy="noload")
    prediction = relationship("PredictionModel", back_populates="comments", lazy="noload")
    replies = relationship("CommentModel", lazy="noload")
