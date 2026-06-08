"""
CrowdIQ — User & Follower ORM Models
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.postgres.models.base import Base, _now, _uuid


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(20), default="user")
    reputation_score: Mapped[int] = mapped_column(Integer, default=0)
    accuracy_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_predictions: Mapped[int] = mapped_column(Integer, default=0)
    resolved_predictions: Mapped[int] = mapped_column(Integer, default=0)
    virtual_points: Mapped[int] = mapped_column(Integer, default=1000)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=_now)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now)

    predictions = relationship("PredictionModel", back_populates="creator", lazy="noload")
    votes = relationship("VoteModel", back_populates="user", lazy="noload")
    comments = relationship("CommentModel", back_populates="user", lazy="noload")
    reputation_history = relationship("ReputationHistoryModel", back_populates="user", lazy="noload")
    wallet_transactions = relationship("WalletTransactionModel", back_populates="user", lazy="noload")
    notifications = relationship("NotificationModel", back_populates="user", lazy="noload")


class FollowerModel(Base):
    __tablename__ = "followers"
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follower_following"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    follower_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    following_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
