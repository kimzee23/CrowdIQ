"""
CrowdIQ — Notification Service
"""
from __future__ import annotations

from typing import List

from src.domain.model.notification import Notification, NotificationType
from src.application.port.output.notification_repository import AbstractNotificationRepository
from src.domain.exception.base import ForbiddenError, NotFoundError
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class NotificationService:
    def __init__(self, notification_repo: AbstractNotificationRepository) -> None:
        self._notifications = notification_repo

    async def push(
        self,
        user_id: str,
        type: NotificationType,
        message: str,
        reference_id: str | None = None,
    ) -> Notification:
        notification = Notification(
            id=generate_uuid(),
            user_id=user_id,
            type=type,
            message=message,
            reference_id=reference_id,
            created_at=utc_now(),
        )
        return await self._notifications.create(notification)

    async def get_user_notifications(
        self,
        user_id: str,
        skip: int,
        limit: int,
        unread_only: bool = False,
    ) -> List[Notification]:
        return await self._notifications.get_by_user(user_id, skip, limit, unread_only)

    async def mark_read(self, user_id: str, notification_id: str | None = None) -> None:
        await self._notifications.mark_read(user_id, notification_id)

    async def delete(self, notification_id: str, requester_id: str) -> None:
        results = await self._notifications.get_by_user(requester_id, skip=0, limit=1)
        # Fetch the single notification to verify ownership
        all_notifs = await self._notifications.get_by_user(requester_id, skip=0, limit=200)
        owned = any(n.id == notification_id for n in all_notifs)
        if not owned:
            raise ForbiddenError("Cannot delete another user's notification")
        await self._notifications.delete(notification_id)
