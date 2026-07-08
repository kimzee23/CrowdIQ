"""
CrowdIQ — Update Comment Use Case
"""
from __future__ import annotations

from src.application.dto.comment import UpdateCommentRequest
from src.domain.model.comment import Comment
from src.application.port.output.comment_repository import AbstractCommentRepository
from src.domain.model.user import User
from src.domain.exception.base import ForbiddenError, NotFoundError
from src.infrastructure.config.utils.helpers import utc_now


class UpdateComment:
    def __init__(self, comment_repo: AbstractCommentRepository) -> None:
        self._comments = comment_repo

    async def execute(
        self, comment_id: str, req: UpdateCommentRequest, requester: User
    ) -> Comment:
        comment = await self._comments.get_by_id(comment_id)
        if not comment:
            raise NotFoundError("Comment", comment_id)
        if comment.user_id != requester.id and not requester.is_moderator_or_above():
            raise ForbiddenError("Cannot edit another user's comment")
        comment.content = req.content
        comment.updated_at = utc_now()
        return await self._comments.update(comment)
