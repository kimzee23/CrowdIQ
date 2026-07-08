"""
CrowdIQ — Trending Predictions Use Case
"""
from __future__ import annotations

from typing import List

from src.domain.model.prediction import Prediction
from src.application.port.output.prediction_repository import AbstractPredictionRepository


class TrendingPredictions:
    def __init__(self, prediction_repo: AbstractPredictionRepository) -> None:
        self._predictions = prediction_repo

    async def execute(self, limit: int = 10) -> List[Prediction]:
        return await self._predictions.get_trending(limit)
