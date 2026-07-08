"""
CrowdIQ — Follow User Use Case
"""
from __future__ import annotations

from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import NotFoundError, SelfFollowError


class FollowUser:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def execute(self, follower_id: str, following_id: str) -> None:
        if follower_id == following_id:
            raise SelfFollowError()
        target = await self._users.get_by_id(following_id)
        if not target:
            raise NotFoundError("User", following_id)
        await self._users.follow(follower_id, following_id)
