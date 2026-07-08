"""
CrowdIQ — Resolve Prediction Use Case
"""
from __future__ import annotations

from src.application.dto.prediction import ResolvePredictionRequest
from src.domain.model.prediction import Prediction, PredictionStatus
from src.application.port.output.prediction_repository import AbstractPredictionRepository
from src.domain.model.user import User
from src.domain.exception.base import ForbiddenError, NotFoundError, PredictionStatusError
from src.infrastructure.config.utils.helpers import utc_now


class ResolvePrediction:
    def __init__(self, prediction_repo: AbstractPredictionRepository) -> None:
        self._predictions = prediction_repo

    async def execute(
        self, prediction_id: str, req: ResolvePredictionRequest, requester: User
    ) -> Prediction:
        pred = await self._get_or_404(prediction_id)
        if not (requester.is_moderator_or_above() or pred.creator_id == requester.id):
            raise ForbiddenError("Only the creator or a moderator can resolve predictions")
        if not pred.can_resolve():
            raise PredictionStatusError("resolve", pred.status.value)
        option_ids = {o.id for o in pred.options}
        if req.winning_option_id not in option_ids:
            raise NotFoundError("Option", req.winning_option_id)
        pred.status = PredictionStatus.RESOLVED
        pred.resolved_option_id = req.winning_option_id
        pred.resolved_at = utc_now()
        pred.updated_at = utc_now()
        return await self._predictions.update(pred)

    async def _get_or_404(self, prediction_id: str) -> Prediction:
        pred = await self._predictions.get_by_id(prediction_id)
        if not pred:
            raise NotFoundError("Prediction", prediction_id)
        return pred
