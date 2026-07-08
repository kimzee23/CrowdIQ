"""
CrowdIQ — PostgreSQL Comment Repository (Adapter)
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.model.comment import Comment
from src.application.port.output.comment_repository import AbstractCommentRepository
from src.infrastructure.persistence.models.comment import CommentModel


class PostgresCommentRepository(AbstractCommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    @staticmethod
    def _to_entity(m: CommentModel) -> Comment:
        return Comment(
            id=m.id,
            prediction_id=m.prediction_id,
            user_id=m.user_id,
            content=m.content,
            parent_id=m.parent_id,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def create(self, comment: Comment) -> Comment:
        m = CommentModel(
            id=comment.id,
            prediction_id=comment.prediction_id,
            user_id=comment.user_id,
            content=comment.content,
            parent_id=comment.parent_id,
        )
        self._s.add(m)
        await self._s.flush()
        return self._to_entity(m)

    async def get_by_id(self, comment_id: str) -> Optional[Comment]:
        r = await self._s.execute(select(CommentModel).where(CommentModel.id == comment_id))
        m = r.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def get_by_prediction(
        self, prediction_id: str, skip: int = 0, limit: int = 50
    ) -> List[Comment]:
        r = await self._s.execute(
            select(CommentModel)
            .where(
                CommentModel.prediction_id == prediction_id,
                CommentModel.parent_id.is_(None),  # top-level only
            )
            .order_by(CommentModel.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in r.scalars().all()]

    async def update(self, comment: Comment) -> Comment:
        await self._s.execute(
            update(CommentModel)
            .where(CommentModel.id == comment.id)
            .values(content=comment.content)
        )
        await self._s.flush()
        return comment

    async def delete(self, comment_id: str) -> None:
        r = await self._s.execute(select(CommentModel).where(CommentModel.id == comment_id))
        m = r.scalar_one_or_none()
        if m:
            await self._s.delete(m)
            await self._s.flush()
