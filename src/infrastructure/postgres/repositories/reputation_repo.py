"""
CrowdIQ — PostgreSQL Reputation & Wallet Repositories (Adapters)
"""
from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.reputation.entity import ReputationHistory, WalletTransaction
from src.domain.reputation.repository import AbstractReputationRepository, AbstractWalletRepository
from src.infrastructure.postgres.models.reputation import ReputationHistoryModel, WalletTransactionModel


class PostgresReputationRepository(AbstractReputationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    @staticmethod
    def _to_entity(m: ReputationHistoryModel) -> ReputationHistory:
        return ReputationHistory(
            id=m.id, user_id=m.user_id, points=m.points, reason=m.reason, created_at=m.created_at
        )

    async def add_history(self, entry: ReputationHistory) -> ReputationHistory:
        m = ReputationHistoryModel(
            id=entry.id, user_id=entry.user_id, points=entry.points, reason=entry.reason
        )
        self._s.add(m)
        await self._s.flush()
        return self._to_entity(m)

    async def get_history(self, user_id: str, skip: int = 0, limit: int = 20) -> List[ReputationHistory]:
        r = await self._s.execute(
            select(ReputationHistoryModel)
            .where(ReputationHistoryModel.user_id == user_id)
            .order_by(ReputationHistoryModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in r.scalars().all()]


class PostgresWalletRepository(AbstractWalletRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    @staticmethod
    def _to_entity(m: WalletTransactionModel) -> WalletTransaction:
        return WalletTransaction(
            id=m.id,
            user_id=m.user_id,
            amount=m.amount,
            reason=m.reason,
            prediction_id=m.prediction_id,
            created_at=m.created_at,
        )

    async def add_transaction(self, tx: WalletTransaction) -> WalletTransaction:
        m = WalletTransactionModel(
            id=tx.id,
            user_id=tx.user_id,
            amount=tx.amount,
            reason=tx.reason,
            prediction_id=tx.prediction_id,
        )
        self._s.add(m)
        await self._s.flush()
        return self._to_entity(m)

    async def get_history(self, user_id: str, skip: int = 0, limit: int = 20) -> List[WalletTransaction]:
        r = await self._s.execute(
            select(WalletTransactionModel)
            .where(WalletTransactionModel.user_id == user_id)
            .order_by(WalletTransactionModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in r.scalars().all()]
