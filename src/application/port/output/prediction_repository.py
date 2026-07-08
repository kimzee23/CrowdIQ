"""
CrowdIQ — Prediction & Category Repository Ports
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.model.prediction import  Prediction

from src.domain.model.category import Category

class AbstractPredictionRepository(ABC):
    @abstractmethod
    async def create(self, prediction: Prediction) -> Prediction: ...

    @abstractmethod
    async def get_by_id(self, prediction_id: str) -> Optional[Prediction]: ...

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> List[Prediction]: ...

    @abstractmethod
    async def update(self, prediction: Prediction) -> Prediction: ...

    @abstractmethod
    async def delete(self, prediction_id: str) -> None: ...

    @abstractmethod
    async def get_trending(self, limit: int = 10) -> List[Prediction]: ...

    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Prediction]: ...

    @abstractmethod
    async def increment_view(self, prediction_id: str) -> None: ...


class AbstractCategoryRepository(ABC):
    @abstractmethod
    async def create(self, category: Category) -> Category: ...

    @abstractmethod
    async def get_by_id(self, category_id: str) -> Optional[Category]: ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Category]: ...

    @abstractmethod
    async def list_all(self) -> List[Category]: ...

    @abstractmethod
    async def update(self, category: Category) -> Category: ...

    @abstractmethod
    async def delete(self, category_id: str) -> None: ...
