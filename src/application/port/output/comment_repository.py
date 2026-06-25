"""
CrowdIQ — Comment Repository Port
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.model.comment import Comment


class AbstractCommentRepository(ABC):
    @abstractmethod
    async def create(self, comment: Comment) -> Comment: ...

    @abstractmethod
    async def get_by_id(self, comment_id: str) -> Optional[Comment]: ...

    @abstractmethod
    async def get_by_prediction(
        self, prediction_id: str, skip: int = 0, limit: int = 50
    ) -> List[Comment]: ...

    @abstractmethod
    async def update(self, comment: Comment) -> Comment: ...

    @abstractmethod
    async def delete(self, comment_id: str) -> None: ...
