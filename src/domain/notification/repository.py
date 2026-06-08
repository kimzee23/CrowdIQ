"""
CrowdIQ — Notification Repository Port
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from src.domain.notification.entity import Notification


class AbstractNotificationRepository(ABC):
    @abstractmethod
    async def create(self, notification: Notification) -> Notification: ...

    @abstractmethod
    async def get_by_user(
        self, user_id: str, skip: int = 0, limit: int = 20, unread_only: bool = False
    ) -> List[Notification]: ...

    @abstractmethod
    async def mark_read(self, user_id: str, notification_id: str | None = None) -> None:
        """Mark one notification (or ALL if notification_id is None) as read."""
        ...

    @abstractmethod
    async def delete(self, notification_id: str) -> None: ...
