"""
CrowdIQ — Send Notification Use Case
"""
from __future__ import annotations

from src.domain.model.notification import Notification, NotificationType
from src.application.port.output.notification_repository import AbstractNotificationRepository
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class SendNotification:
    def __init__(self, notification_repo: AbstractNotificationRepository) -> None:
        self._notifications = notification_repo

    async def execute(
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
