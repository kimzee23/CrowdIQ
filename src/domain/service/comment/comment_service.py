"""
CrowdIQ — Comment Service
"""
from __future__ import annotations

from typing import List

from src.application.dto.comment import CreateCommentRequest, UpdateCommentRequest
from src.domain.model.comment import Comment
from src.application.port.output.comment_repository import AbstractCommentRepository
from src.application.port.output.prediction_repository import AbstractPredictionRepository
from src.domain.model.user import User
from src.domain.exception.base import ForbiddenError, NotFoundError
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class CommentService:
    def __init__(
        self,
        comment_repo: AbstractCommentRepository,
        prediction_repo: AbstractPredictionRepository,
    ) -> None:
        self._comments = comment_repo
        self._predictions = prediction_repo

    async def create_comment(self, req: CreateCommentRequest, author: User) -> Comment:
        pred = await self._predictions.get_by_id(req.prediction_id)
        if not pred:
            raise NotFoundError("Prediction", req.prediction_id)

        if req.parent_id:
            parent = await self._comments.get_by_id(req.parent_id)
            if not parent or parent.prediction_id != req.prediction_id:
                raise NotFoundError("Parent comment", req.parent_id)

        comment = Comment(
            id=generate_uuid(),
            prediction_id=req.prediction_id,
            user_id=author.id,
            content=req.content,
            parent_id=req.parent_id,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        return await self._comments.create(comment)

    async def update_comment(
        self, comment_id: str, req: UpdateCommentRequest, requester: User
    ) -> Comment:
        comment = await self._get_or_404(comment_id)
        if comment.user_id != requester.id and not requester.is_moderator_or_above():
            raise ForbiddenError("Cannot edit another user's comment")
        comment.content = req.content
        comment.updated_at = utc_now()
        return await self._comments.update(comment)

    async def delete_comment(self, comment_id: str, requester: User) -> None:
        comment = await self._get_or_404(comment_id)
        if comment.user_id != requester.id and not requester.is_moderator_or_above():
            raise ForbiddenError("Cannot delete another user's comment")
        await self._comments.delete(comment_id)

    async def get_comments(
        self, prediction_id: str, skip: int, limit: int
    ) -> List[Comment]:
        pred = await self._predictions.get_by_id(prediction_id)
        if not pred:
            raise NotFoundError("Prediction", prediction_id)
        return await self._comments.get_by_prediction(prediction_id, skip, limit)

    async def _get_or_404(self, comment_id: str) -> Comment:
        c = await self._comments.get_by_id(comment_id)
        if not c:
            raise NotFoundError("Comment", comment_id)
        return c
