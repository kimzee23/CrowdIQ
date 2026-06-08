"""
CrowdIQ — User Service
"""
from __future__ import annotations

from src.application.dto.user import UpdateUserRequest
from src.domain.user.entity import User
from src.domain.user.repository import AbstractUserRepository
from src.shared.exceptions.base import ForbiddenError, NotFoundError, SelfFollowError
from src.shared.utils.helpers import utc_now


class UserService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def get_user(self, user_id: str) -> User:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user

    async def update_user(self, user_id: str, req: UpdateUserRequest, requester_id: str) -> User:
        if user_id != requester_id:
            raise ForbiddenError("Cannot edit another user's profile")
        user = await self.get_user(user_id)
        if req.display_name is not None:
            user.display_name = req.display_name
        if req.avatar_url is not None:
            user.avatar_url = req.avatar_url
        if req.bio is not None:
            user.bio = req.bio
        user.updated_at = utc_now()
        return await self._users.update(user)

    async def delete_user(self, user_id: str, requester: User) -> None:
        if user_id != requester.id and not requester.is_admin():
            raise ForbiddenError("Cannot delete another user's account")
        await self._users.delete(user_id)

    async def search_users(self, query: str, skip: int, limit: int) -> list[User]:
        return await self._users.search(query, skip, limit)

    async def get_leaderboard(self, skip: int, limit: int, category_slug: str | None) -> list[User]:
        return await self._users.get_leaderboard(skip, limit, category_slug)

    async def follow(self, follower_id: str, following_id: str) -> None:
        if follower_id == following_id:
            raise SelfFollowError()
        await self.get_user(following_id)  # ensure target exists
        await self._users.follow(follower_id, following_id)

    async def unfollow(self, follower_id: str, following_id: str) -> None:
        await self._users.unfollow(follower_id, following_id)

    async def get_followers(self, user_id: str, skip: int, limit: int) -> list[User]:
        await self.get_user(user_id)
        return await self._users.get_followers(user_id, skip, limit)

    async def get_following(self, user_id: str, skip: int, limit: int) -> list[User]:
        await self.get_user(user_id)
        return await self._users.get_following(user_id, skip, limit)

    async def is_following(self, follower_id: str, following_id: str) -> bool:
        return await self._users.is_following(follower_id, following_id)
