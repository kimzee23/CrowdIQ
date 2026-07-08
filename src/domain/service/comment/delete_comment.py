"""
CrowdIQ — Delete Comment Use Case
"""
from __future__ import annotations

from src.application.port.output.comment_repository import AbstractCommentRepository
from src.domain.model.user import User
from src.domain.exception.base import ForbiddenError, NotFoundError


class DeleteComment:
    def __init__(self, comment_repo: AbstractCommentRepository) -> None:
        self._comments = comment_repo

    async def execute(self, comment_id: str, requester: User) -> None:
        comment = await self._comments.get_by_id(comment_id)
        if not comment:
            raise NotFoundError("Comment", comment_id)
        if comment.user_id != requester.id and not requester.is_moderator_or_above():
            raise ForbiddenError("Cannot delete another user's comment")
        await self._comments.delete(comment_id)
