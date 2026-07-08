"""
CrowdIQ — Update Category Use Case
"""
from __future__ import annotations

from slugify import slugify

from src.application.dto.prediction import UpdateCategoryRequest
from src.domain.model.prediction import Category
from src.application.port.output.prediction_repository import AbstractCategoryRepository
from src.domain.model.user import User
from src.domain.exception.base import ForbiddenError, NotFoundError


class UpdateCategory:
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self._categories = category_repo

    async def execute(
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
