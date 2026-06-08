"""
CrowdIQ — Vote Repository Port
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.vote.entity import Vote


class AbstractVoteRepository(ABC):
    @abstractmethod
    async def create(self, vote: Vote) -> Vote: ...

    @abstractmethod
    async def get_by_id(self, vote_id: str) -> Optional[Vote]: ...

    @abstractmethod
    async def get_by_user_and_prediction(
        self, user_id: str, prediction_id: str
    ) -> Optional[Vote]: ...

    @abstractmethod
    async def get_by_prediction(
        self, prediction_id: str, skip: int = 0, limit: int = 50
    ) -> List[Vote]: ...

    @abstractmethod
    async def get_by_user(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> List[Vote]: ...

    @abstractmethod
    async def update_stake(self, vote_id: str, stake: int) -> Vote: ...
