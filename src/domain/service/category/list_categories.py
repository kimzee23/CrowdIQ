"""
CrowdIQ — List Categories Use Case
"""
from __future__ import annotations

from typing import List

from src.domain.model.prediction import Category
from src.application.port.output.prediction_repository import AbstractCategoryRepository


class ListCategories:
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self._categories = category_repo

    async def execute(self) -> List[Category]:
        return await self._categories.list_all()
