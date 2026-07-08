"""
CrowdIQ — Create Prediction Use Case
"""
from __future__ import annotations

from src.application.dto.prediction import CreatePredictionRequest
from src.domain.model.prediction import Prediction, PredictionOption, PredictionStatus
from src.application.port.output.prediction_repository import (
    AbstractCategoryRepository,
    AbstractPredictionRepository,
)
from src.domain.model.user import User
from src.domain.exception.base import NotFoundError
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class CreatePrediction:
    def __init__(
        self,
        prediction_repo: AbstractPredictionRepository,
        category_repo: AbstractCategoryRepository,
    ) -> None:
        self._predictions = prediction_repo
        self._categories = category_repo

    async def execute(self, req: CreatePredictionRequest, creator: User) -> Prediction:
        if not await self._categories.get_by_id(req.category_id):
            raise NotFoundError("Category", req.category_id)

        prediction_id = generate_uuid()
        options = [
            PredictionOption(
                id=generate_uuid(),
                prediction_id=prediction_id,
                option_text=opt.option_text,
            )
            for opt in req.options
        ]
        prediction = Prediction(
            id=prediction_id,
            creator_id=creator.id,
            title=req.title,
            description=req.description,
            category_id=req.category_id,
            prediction_type=req.prediction_type,
            status=PredictionStatus.OPEN,
            options=options,
            close_at=req.close_at,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        return await self._predictions.create(prediction)
