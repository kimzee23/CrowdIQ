"""
CrowdIQ — PostgreSQL Notification Repository (Adapter)
"""
from __future__ import annotations

from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.notification.entity import Notification, NotificationType
from src.domain.notification.repository import AbstractNotificationRepository
from src.infrastructure.postgres.models.notification import NotificationModel


class PostgresNotificationRepository(AbstractNotificationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    @staticmethod
    def _to_entity(m: NotificationModel) -> Notification:
        return Notification(
            id=m.id,
            user_id=m.user_id,
            type=NotificationType(m.type),
            message=m.message,
            is_read=m.is_read,
            reference_id=m.reference_id,
            created_at=m.created_at,
        )

    async def create(self, notification: Notification) -> Notification:
        m = NotificationModel(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type.value,
            message=notification.message,
            is_read=notification.is_read,
            reference_id=notification.reference_id,
        )
        self._s.add(m)
        await self._s.flush()
        return self._to_entity(m)

    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
    ) -> List[Notification]:
        stmt = select(NotificationModel).where(NotificationModel.user_id == user_id)
        if unread_only:
            stmt = stmt.where(NotificationModel.is_read.is_(False))
        stmt = stmt.order_by(NotificationModel.created_at.desc()).offset(skip).limit(limit)
        r = await self._s.execute(stmt)
        return [self._to_entity(m) for m in r.scalars().all()]

    async def mark_read(self, user_id: str, notification_id: str | None = None) -> None:
        stmt = update(NotificationModel).where(NotificationModel.user_id == user_id)
        if notification_id:
            stmt = stmt.where(NotificationModel.id == notification_id)
        await self._s.execute(stmt.values(is_read=True))
        await self._s.flush()

    async def delete(self, notification_id: str) -> None:
        r = await self._s.execute(
            select(NotificationModel).where(NotificationModel.id == notification_id)
        )
        m = r.scalar_one_or_none()
        if m:
            await self._s.delete(m)
            await self._s.flush()
