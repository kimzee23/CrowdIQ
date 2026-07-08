"""
CrowdIQ — Create Category Use Case
"""
from __future__ import annotations

from slugify import slugify

from src.application.dto.prediction import CreateCategoryRequest
from src.domain.model.prediction import Category
from src.application.port.output.prediction_repository import AbstractCategoryRepository
from src.domain.model.user import User
from src.domain.exception.base import ConflictError, ForbiddenError
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class CreateCategory:
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self._categories = category_repo

    async def execute(self, req: CreateCategoryRequest, requester: User) -> Category:
        if not requester.is_admin():
            raise ForbiddenError("Only admins can create categories")
        slug = slugify(req.name)
        if await self._categories.get_by_slug(slug):
            raise ConflictError(f"Category '{req.name}' already exists")
        cat = Category(id=generate_uuid(), name=req.name, slug=slug, created_at=utc_now())
        return await self._categories.create(cat)
