"""
CrowdIQ — Unfollow User Use Case
"""
from __future__ import annotations

from src.application.port.output.user_repository import AbstractUserRepository


class UnfollowUser:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def execute(self, follower_id: str, following_id: str) -> None:
        await self._users.unfollow(follower_id, following_id)
