"""
CrowdIQ — User Repository Port (Abstract Interface)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.model.user import User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]: ...

    @abstractmethod
    async def get_by_display_name(self, display_name: str) -> Optional[User]: ...


    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: str) -> None: ...

    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 20) -> List[User]: ...

    @abstractmethod
    async def get_leaderboard(
        self,
        skip: int = 0,
        limit: int = 20,
        category_slug: Optional[str] = None,
    ) -> List[User]: ...

    @abstractmethod
    async def follow(self, follower_id: str, following_id: str) -> None: ...

    @abstractmethod
    async def unfollow(self, follower_id: str, following_id: str) -> None: ...

    @abstractmethod
    async def get_followers(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> List[User]: ...

    @abstractmethod
    async def get_following(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> List[User]: ...

    @abstractmethod
    async def is_following(self, follower_id: str, following_id: str) -> bool: ...
