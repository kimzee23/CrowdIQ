"""
CrowdIQ — Delete Prediction Use Case
"""
from __future__ import annotations

from src.domain.model.prediction import Prediction
from src.application.port.output.prediction_repository import AbstractPredictionRepository
from src.domain.model.user import User
from src.domain.exception.base import ForbiddenError, NotFoundError


class DeletePrediction:
    def __init__(self, prediction_repo: AbstractPredictionRepository) -> None:
        self._predictions = prediction_repo

    async def execute(self, prediction_id: str, requester: User) -> None:
        pred = await self._get_or_404(prediction_id)
        self._check_ownership(pred, requester)
        await self._predictions.delete(prediction_id)

    async def _get_or_404(self, prediction_id: str) -> Prediction:
        pred = await self._predictions.get_by_id(prediction_id)
        if not pred:
            raise NotFoundError("Prediction", prediction_id)
        return pred

    @staticmethod
    def _check_ownership(pred: Prediction, requester: User) -> None:
        if pred.creator_id != requester.id and not requester.is_moderator_or_above():
            raise ForbiddenError("You do not own this prediction")
