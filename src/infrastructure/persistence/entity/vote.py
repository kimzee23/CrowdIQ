"""
CrowdIQ — Vote ORM Model
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.entity.base import Base, _now, _uuid


class VoteModel(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("user_id", "prediction_id", name="uq_user_prediction_vote"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prediction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    option_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("prediction_options.id"), nullable=False
    )
    confidence: Mapped[int] = mapped_column(Integer, default=50)
    stake: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=_now)

    user = relationship("UserModel", back_populates="votes", lazy="noload")
    prediction = relationship("PredictionModel", back_populates="votes", lazy="noload")
    option = relationship("PredictionOptionModel", lazy="noload")
