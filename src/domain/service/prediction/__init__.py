"""
CrowdIQ — Prediction Service Package

Re-exports the backwards-compatible PredictionService facade and
exposes all individual use-case classes.
"""
from __future__ import annotations

from typing import List, Optional

from slugify import slugify

from src.application.dto.prediction import (
    CreateCategoryRequest,
    CreatePredictionRequest,
    ResolvePredictionRequest,
    UpdateCategoryRequest,
    UpdatePredictionRequest,
)
from src.domain.model.category import Category
from src.domain.model.prediction import Prediction, PredictionStatus
from src.application.port.output.prediction_repository import (
    AbstractCategoryRepository,
    AbstractPredictionRepository,
)
from src.domain.model.user import User
from src.domain.exception.base import ConflictError, ForbiddenError, NotFoundError
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now

from src.domain.service.prediction.create_prediction import CreatePrediction
from src.domain.service.prediction.get_prediction import GetPrediction
from src.domain.service.prediction.list_predictions import ListPredictions
from src.domain.service.prediction.update_prediction import UpdatePrediction
from src.domain.service.prediction.delete_prediction import DeletePrediction
from src.domain.service.prediction.close_prediction import ClosePrediction
from src.domain.service.prediction.resolve_prediction import ResolvePrediction
from src.domain.service.prediction.trending_predictions import TrendingPredictions


class PredictionService:
    """
    Facade composing all prediction & category use cases.
    Kept for DI backwards-compatibility; prefer individual use-case classes
    for new code.
    """

    def __init__(
        self,
        prediction_repo: AbstractPredictionRepository,
        category_repo: AbstractCategoryRepository,
    ) -> None:
        self._predictions = prediction_repo
        self._categories = category_repo
        self._create = CreatePrediction(prediction_repo, category_repo)
        self._get = GetPrediction(prediction_repo)
        self._list = ListPredictions(prediction_repo)
        self._update = UpdatePrediction(prediction_repo, category_repo)
        self._delete = DeletePrediction(prediction_repo)
        self._close = ClosePrediction(prediction_repo)
        self._resolve = ResolvePrediction(prediction_repo)
        self._trending = TrendingPredictions(prediction_repo)

    async def create(self, req: CreatePredictionRequest, creator: User) -> Prediction:
        return await self._create.execute(req, creator)

    async def get(self, prediction_id: str) -> Prediction:
        return await self._get.execute(prediction_id)

    async def list_all(
        self,
        skip: int,
        limit: int,
        status: Optional[str],
        category_id: Optional[str],
    ) -> List[Prediction]:
        return await self._list.execute(skip, limit, status, category_id)

    async def update(
        self, prediction_id: str, req: UpdatePredictionRequest, requester: User
    ) -> Prediction:
        return await self._update.execute(prediction_id, req, requester)

    async def delete(self, prediction_id: str, requester: User) -> None:
        return await self._delete.execute(prediction_id, requester)

    async def close(self, prediction_id: str, requester: User) -> Prediction:
        return await self._close.execute(prediction_id, requester)

    async def resolve(
        self, prediction_id: str, req: ResolvePredictionRequest, requester: User
    ) -> Prediction:
        return await self._resolve.execute(prediction_id, req, requester)

    async def get_trending(self, limit: int = 10) -> List[Prediction]:
        return await self._trending.execute(limit)

    # ── Category Management ───────────────────────────────────────────────────

    async def list_categories(self) -> List[Category]:
        return await self._categories.list_all()

    async def create_category(self, req: CreateCategoryRequest, requester: User) -> Category:
        if not requester.is_admin():
            raise ForbiddenError("Only admins can create categories")
        slug = slugify(req.name)
        if await self._categories.get_by_slug(slug):
            raise ConflictError(f"Category '{req.name}' already exists")
        cat = Category(id=generate_uuid(), name=req.name, slug=slug, created_at=utc_now())
        return await self._categories.create(cat)

    async def update_category(
        self, category_id: str, req: UpdateCategoryRequest, requester: User
    ) -> Category:
        if not requester.is_admin():
            raise ForbiddenError("Only admins can update categories")
        cat = await self._categories.get_by_id(category_id)
        if not cat:
            raise NotFoundError("Category", category_id)
        cat.name = req.name
        cat.slug = slugify(req.name)
        return await self._categories.update(cat)

    async def delete_category(self, category_id: str, requester: User) -> None:
        if not requester.is_admin():
            raise ForbiddenError("Only admins can delete categories")
        cat = await self._categories.get_by_id(category_id)
        if not cat:
            raise NotFoundError("Category", category_id)
        await self._categories.delete(category_id)


__all__ = [
    "PredictionService",
    "CreatePrediction",
    "GetPrediction",
    "ListPredictions",
    "UpdatePrediction",
    "DeletePrediction",
    "ClosePrediction",
    "ResolvePrediction",
    "TrendingPredictions",
]
