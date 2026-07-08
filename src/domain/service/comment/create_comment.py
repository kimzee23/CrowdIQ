"""
CrowdIQ — Create Comment Use Case
"""
from __future__ import annotations

from src.application.dto.comment import CreateCommentRequest
from src.domain.model.comment import Comment
from src.application.port.output.comment_repository import AbstractCommentRepository
from src.application.port.output.prediction_repository import AbstractPredictionRepository
from src.domain.model.user import User
from src.domain.exception.base import NotFoundError
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class CreateComment:
    def __init__(
        self,
        comment_repo: AbstractCommentRepository,
        prediction_repo: AbstractPredictionRepository,
    ) -> None:
        self._comments = comment_repo
        self._predictions = prediction_repo

    async def execute(self, req: CreateCommentRequest, author: User) -> Comment:
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
