"""
CrowdIQ — Delete Category Use Case
"""
from __future__ import annotations

from src.application.port.output.prediction_repository import AbstractCategoryRepository
from src.domain.model.user import User
from src.domain.exception.base import ForbiddenError, NotFoundError


class DeleteCategory:
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self._categories = category_repo

    async def execute(self, category_id: str, requester: User) -> None:
        if not requester.is_admin():
            raise ForbiddenError("Only admins can delete categories")
        cat = await self._categories.get_by_id(category_id)
        if not cat:
            raise NotFoundError("Category", category_id)
        await self._categories.delete(category_id)
