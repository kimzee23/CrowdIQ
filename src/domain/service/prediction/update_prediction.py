"""
CrowdIQ — Update Prediction Use Case
"""
from __future__ import annotations

from src.application.dto.prediction import UpdatePredictionRequest
from src.domain.model.prediction import Prediction
from src.application.port.output.prediction_repository import (
    AbstractCategoryRepository,
    AbstractPredictionRepository,
)
from src.domain.model.user import User
from src.domain.exception.base import ForbiddenError, NotFoundError, PredictionStatusError
from src.infrastructure.config.utils.helpers import utc_now


class UpdatePrediction:
    def __init__(
        self,
        prediction_repo: AbstractPredictionRepository,
        category_repo: AbstractCategoryRepository,
    ) -> None:
        self._predictions = prediction_repo
        self._categories = category_repo

    async def execute(
        self, prediction_id: str, req: UpdatePredictionRequest, requester: User
    ) -> Prediction:
        pred = await self._get_or_404(prediction_id)
        self._check_ownership(pred, requester)
        if not pred.can_edit():
            raise PredictionStatusError("edit", pred.status.value)
        if req.title is not None:
            pred.title = req.title
        if req.description is not None:
            pred.description = req.description
        if req.category_id is not None:
            if not await self._categories.get_by_id(req.category_id):
                raise NotFoundError("Category", req.category_id)
            pred.category_id = req.category_id
        if req.close_at is not None:
            pred.close_at = req.close_at
        pred.updated_at = utc_now()
        return await self._predictions.update(pred)

    async def _get_or_404(self, prediction_id: str) -> Prediction:
        pred = await self._predictions.get_by_id(prediction_id)
        if not pred:
            raise NotFoundError("Prediction", prediction_id)
        return pred

    @staticmethod
    def _check_ownership(pred: Prediction, requester: User) -> None:
        if pred.creator_id != requester.id and not requester.is_moderator_or_above():
            raise ForbiddenError("You do not own this prediction")
