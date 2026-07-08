"""
CrowdIQ — Update User Profile Use Case
"""
from __future__ import annotations

from src.application.dto.user import UpdateUserRequest
from src.domain.model.user import User
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import ForbiddenError, NotFoundError
from src.infrastructure.config.utils.helpers import utc_now


class UpdateProfile:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def execute(
        self, user_id: str, req: UpdateUserRequest, requester_id: str
    ) -> User:
        if user_id != requester_id:
            raise ForbiddenError("Cannot edit another user's profile")
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        if req.display_name is not None:
            user.display_name = req.display_name
        if req.avatar_url is not None:
            user.avatar_url = req.avatar_url
        if req.bio is not None:
            user.bio = req.bio
        user.updated_at = utc_now()
        return await self._users.update(user)
