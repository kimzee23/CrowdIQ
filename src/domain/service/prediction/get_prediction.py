"""
CrowdIQ — Get Prediction Use Case
"""
from __future__ import annotations

from src.domain.model.prediction import Prediction
from src.application.port.output.prediction_repository import AbstractPredictionRepository
from src.domain.exception.base import NotFoundError


class GetPrediction:
    def __init__(self, prediction_repo: AbstractPredictionRepository) -> None:
        self._predictions = prediction_repo

    async def execute(self, prediction_id: str) -> Prediction:
        pred = await self._predictions.get_by_id(prediction_id)
        if not pred:
            raise NotFoundError("Prediction", prediction_id)
        await self._predictions.increment_view(prediction_id)
        pred.view_count += 1
        return pred
