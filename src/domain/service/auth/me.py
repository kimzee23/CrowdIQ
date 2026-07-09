"""
CrowdIQ — Me Service
Fetches the currently authenticated user's profile.
"""
from __future__ import annotations

from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import NotFoundError
from src.domain.model.user import User


class MeService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def __call__(self, user_id: str) -> User:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user
