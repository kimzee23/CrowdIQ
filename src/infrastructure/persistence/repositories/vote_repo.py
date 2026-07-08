"""
CrowdIQ — PostgreSQL Vote Repository (Adapter)
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.model.vote import Vote
from src.application.port.output.vote_repository import AbstractVoteRepository
from src.infrastructure.persistence.models.vote import VoteModel


class PostgresVoteRepository(AbstractVoteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    @staticmethod
    def _to_entity(m: VoteModel) -> Vote:
        return Vote(
            id=m.id,
            user_id=m.user_id,
            prediction_id=m.prediction_id,
            option_id=m.option_id,
            confidence=m.confidence,
            stake=m.stake,
            created_at=m.created_at,
        )

    async def create(self, vote: Vote) -> Vote:
        m = VoteModel(
            id=vote.id,
            user_id=vote.user_id,
            prediction_id=vote.prediction_id,
            option_id=vote.option_id,
            confidence=vote.confidence,
            stake=vote.stake,
        )
        self._s.add(m)
        await self._s.flush()
        return self._to_entity(m)

    async def get_by_id(self, vote_id: str) -> Optional[Vote]:
        r = await self._s.execute(select(VoteModel).where(VoteModel.id == vote_id))
        m = r.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def get_by_user_and_prediction(self, user_id: str, prediction_id: str) -> Optional[Vote]:
        r = await self._s.execute(
            select(VoteModel).where(
                VoteModel.user_id == user_id,
                VoteModel.prediction_id == prediction_id,
            )
        )
        m = r.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def get_by_prediction(
        self, prediction_id: str, skip: int = 0, limit: int = 50
    ) -> List[Vote]:
        r = await self._s.execute(
            select(VoteModel)
            .where(VoteModel.prediction_id == prediction_id)
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in r.scalars().all()]

    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Vote]:
        r = await self._s.execute(
            select(VoteModel)
            .where(VoteModel.user_id == user_id)
            .order_by(VoteModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in r.scalars().all()]

    async def update_stake(self, vote_id: str, stake: int) -> Vote:
        await self._s.execute(
            update(VoteModel).where(VoteModel.id == vote_id).values(stake=stake)
        )
        await self._s.flush()
        vote = await self.get_by_id(vote_id)
        return vote  # type: ignore[return-value]
