"""
CrowdIQ — Mark Notification as Read Use Case
"""
from __future__ import annotations

from src.application.port.output.notification_repository import AbstractNotificationRepository


class MarkAsRead:
    def __init__(self, notification_repo: AbstractNotificationRepository) -> None:
        self._notifications = notification_repo

    async def execute(self, user_id: str, notification_id: str | None = None) -> None:
        await self._notifications.mark_read(user_id, notification_id)
