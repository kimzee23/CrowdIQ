"""
CrowdIQ — PostgreSQL Prediction & Category Repositories (Adapters)
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.prediction.entity import Category, Prediction, PredictionOption, PredictionStatus, PredictionType
from src.domain.prediction.repository import AbstractCategoryRepository, AbstractPredictionRepository
from src.infrastructure.postgres.models.prediction import CategoryModel, PredictionModel, PredictionOptionModel


class PostgresPredictionRepository(AbstractPredictionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    @staticmethod
    def _option_to_entity(m: PredictionOptionModel) -> PredictionOption:
        return PredictionOption(
            id=m.id,
            prediction_id=m.prediction_id,
            option_text=m.option_text,
            vote_count=m.vote_count,
        )

    @staticmethod
    def _to_entity(m: PredictionModel, options: List[PredictionOptionModel]) -> Prediction:
        return Prediction(
            id=m.id,
            creator_id=m.creator_id,
            title=m.title,
            description=m.description,
            category_id=m.category_id,
            prediction_type=PredictionType(m.prediction_type),
            status=PredictionStatus(m.status),
            options=[PostgresPredictionRepository._option_to_entity(o) for o in options],
            close_at=m.close_at,
            resolved_at=m.resolved_at,
            resolved_option_id=m.resolved_option_id,
            view_count=m.view_count,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def _get_model_with_options(self, prediction_id: str) -> Optional[tuple]:
        r = await self._s.execute(
            select(PredictionModel)
            .options(selectinload(PredictionModel.options))
            .where(PredictionModel.id == prediction_id)
        )
        m = r.scalar_one_or_none()
        if not m:
            return None
        return m, m.options

    async def create(self, prediction: Prediction) -> Prediction:
        model = PredictionModel(
            id=prediction.id,
            creator_id=prediction.creator_id,
            title=prediction.title,
            description=prediction.description,
            category_id=prediction.category_id,
            prediction_type=prediction.prediction_type.value,
            status=prediction.status.value,
            close_at=prediction.close_at,
            resolved_at=prediction.resolved_at,
            resolved_option_id=prediction.resolved_option_id,
        )
        self._s.add(model)
        await self._s.flush()

        for opt in prediction.options:
            self._s.add(
                PredictionOptionModel(
                    id=opt.id,
                    prediction_id=model.id,
                    option_text=opt.option_text,
                )
            )
        await self._s.flush()
        return prediction

    async def get_by_id(self, prediction_id: str) -> Optional[Prediction]:
        result = await self._get_model_with_options(prediction_id)
        if not result:
            return None
        m, options = result
        return self._to_entity(m, options)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> List[Prediction]:
        stmt = select(PredictionModel).options(selectinload(PredictionModel.options))
        if status:
            stmt = stmt.where(PredictionModel.status == status)
        if category_id:
            stmt = stmt.where(PredictionModel.category_id == category_id)
        stmt = stmt.order_by(PredictionModel.created_at.desc()).offset(skip).limit(limit)
        r = await self._s.execute(stmt)
        return [self._to_entity(m, m.options) for m in r.scalars().all()]

    async def update(self, prediction: Prediction) -> Prediction:
        await self._s.execute(
            update(PredictionModel)
            .where(PredictionModel.id == prediction.id)
            .values(
                title=prediction.title,
                description=prediction.description,
                category_id=prediction.category_id,
                status=prediction.status.value,
                close_at=prediction.close_at,
                resolved_at=prediction.resolved_at,
                resolved_option_id=prediction.resolved_option_id,
                view_count=prediction.view_count,
            )
        )
        await self._s.flush()
        return prediction

    async def delete(self, prediction_id: str) -> None:
        r = await self._s.execute(
            select(PredictionModel).where(PredictionModel.id == prediction_id)
        )
        m = r.scalar_one_or_none()
        if m:
            await self._s.delete(m)
            await self._s.flush()

    async def get_trending(self, limit: int = 10) -> List[Prediction]:
        stmt = (
            select(PredictionModel)
            .options(selectinload(PredictionModel.options))
            .where(PredictionModel.status == PredictionStatus.OPEN.value)
            .order_by(PredictionModel.view_count.desc())
            .limit(limit)
        )
        r = await self._s.execute(stmt)
        return [self._to_entity(m, m.options) for m in r.scalars().all()]

    async def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Prediction]:
        stmt = (
            select(PredictionModel)
            .options(selectinload(PredictionModel.options))
            .where(PredictionModel.title.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
        )
        r = await self._s.execute(stmt)
        return [self._to_entity(m, m.options) for m in r.scalars().all()]

    async def increment_view(self, prediction_id: str) -> None:
        await self._s.execute(
            update(PredictionModel)
            .where(PredictionModel.id == prediction_id)
            .values(view_count=PredictionModel.view_count + 1)
        )
        await self._s.flush()


class PostgresCategoryRepository(AbstractCategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    @staticmethod
    def _to_entity(m: CategoryModel) -> Category:
        return Category(id=m.id, name=m.name, slug=m.slug, created_at=m.created_at)

    async def create(self, category: Category) -> Category:
        m = CategoryModel(id=category.id, name=category.name, slug=category.slug)
        self._s.add(m)
        await self._s.flush()
        return self._to_entity(m)

    async def get_by_id(self, category_id: str) -> Optional[Category]:
        r = await self._s.execute(select(CategoryModel).where(CategoryModel.id == category_id))
        m = r.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        r = await self._s.execute(select(CategoryModel).where(CategoryModel.slug == slug))
        m = r.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def list_all(self) -> List[Category]:
        r = await self._s.execute(select(CategoryModel).order_by(CategoryModel.name))
        return [self._to_entity(m) for m in r.scalars().all()]

    async def update(self, category: Category) -> Category:
        await self._s.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category.id)
            .values(name=category.name, slug=category.slug)
        )
        await self._s.flush()
        return category

    async def delete(self, category_id: str) -> None:
        r = await self._s.execute(select(CategoryModel).where(CategoryModel.id == category_id))
        m = r.scalar_one_or_none()
        if m:
            await self._s.delete(m)
            await self._s.flush()
