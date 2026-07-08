"""
CrowdIQ — List Predictions Use Case
"""
from __future__ import annotations

from typing import List, Optional

from src.domain.model.prediction import Prediction
from src.application.port.output.prediction_repository import AbstractPredictionRepository


class ListPredictions:
    def __init__(self, prediction_repo: AbstractPredictionRepository) -> None:
        self._predictions = prediction_repo

    async def execute(
        self,
        skip: int,
        limit: int,
        status: Optional[str],
        category_id: Optional[str],
    ) -> List[Prediction]:
        return await self._predictions.list_all(skip, limit, status, category_id)
