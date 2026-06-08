"""
CrowdIQ — Search Service
Delegates to existing repositories; wires together cross-domain search.
"""
from __future__ import annotations

from typing import List

from src.domain.prediction.entity import Prediction
from src.domain.prediction.repository import AbstractPredictionRepository
from src.domain.user.entity import User
from src.domain.user.repository import AbstractUserRepository


class SearchService:
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        prediction_repo: AbstractPredictionRepository,
    ) -> None:
        self._users = user_repo
        self._predictions = prediction_repo

    async def search_all(self, query: str, skip: int, limit: int) -> dict:
        users = await self._users.search(query, 0, 5)
        predictions = await self._predictions.search(query, 0, 5)
        return {
            "query": query,
            "users": users,
            "predictions": predictions,
        }

    async def search_users(self, query: str, skip: int, limit: int) -> List[User]:
        return await self._users.search(query, skip, limit)

    async def search_predictions(self, query: str, skip: int, limit: int) -> List[Prediction]:
        return await self._predictions.search(query, skip, limit)
