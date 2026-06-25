"""
CrowdIQ — Prediction Service
"""
from __future__ import annotations

from typing import List, Optional

from slugify import slugify

from src.application.port.input.prediction import (
    CreateCategoryRequest,
    CreatePredictionRequest,
    ResolvePredictionRequest,
    UpdateCategoryRequest,
    UpdatePredictionRequest,
)
from src.domain.model.prediction import (
    Category,
    Prediction,
    PredictionOption,
    PredictionStatus,
)
from src.application.port.output.prediction_repository import AbstractCategoryRepository, AbstractPredictionRepository
from src.domain.model.user import User
from src.domain.exception.base import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    PredictionStatusError,
)
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class PredictionService:
    def __init__(
        self,
        prediction_repo: AbstractPredictionRepository,
        category_repo: AbstractCategoryRepository,
    ) -> None:
        self._predictions = prediction_repo
        self._categories = category_repo

    async def create(self, req: CreatePredictionRequest, creator: User) -> Prediction:
        await self._validate_category(req.category_id)
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

    async def get(self, prediction_id: str) -> Prediction:
        pred = await self._predictions.get_by_id(prediction_id)
        if not pred:
            raise NotFoundError("Prediction", prediction_id)
        await self._predictions.increment_view(prediction_id)
        pred.view_count += 1
        return pred

    async def list_all(
        self,
        skip: int,
        limit: int,
        status: Optional[str],
        category_id: Optional[str],
    ) -> List[Prediction]:
        return await self._predictions.list_all(skip, limit, status, category_id)

    async def update(
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
            await self._validate_category(req.category_id)
            pred.category_id = req.category_id
        if req.close_at is not None:
            pred.close_at = req.close_at
        pred.updated_at = utc_now()
        return await self._predictions.update(pred)

    async def delete(self, prediction_id: str, requester: User) -> None:
        pred = await self._get_or_404(prediction_id)
        self._check_ownership(pred, requester)
        await self._predictions.delete(prediction_id)

    async def close(self, prediction_id: str, requester: User) -> Prediction:
        pred = await self._get_or_404(prediction_id)
        self._check_ownership(pred, requester)
        if not pred.can_close():
            raise PredictionStatusError("close", pred.status.value)
        pred.status = PredictionStatus.AWAITING_RESOLUTION
        pred.updated_at = utc_now()
        return await self._predictions.update(pred)

    async def resolve(
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

    async def get_trending(self, limit: int = 10) -> List[Prediction]:
        return await self._predictions.get_trending(limit)

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

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _get_or_404(self, prediction_id: str) -> Prediction:
        pred = await self._predictions.get_by_id(prediction_id)
        if not pred:
            raise NotFoundError("Prediction", prediction_id)
        return pred

    async def _validate_category(self, category_id: str) -> None:
        if not await self._categories.get_by_id(category_id):
            raise NotFoundError("Category", category_id)

    @staticmethod
    def _check_ownership(pred: Prediction, requester: User) -> None:
        if pred.creator_id != requester.id and not requester.is_moderator_or_above():
            raise ForbiddenError("You do not own this prediction")
