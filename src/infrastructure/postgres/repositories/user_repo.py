"""
CrowdIQ — PostgreSQL User Repository (Adapter)
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user.entity import User, UserRole
from src.domain.user.repository import AbstractUserRepository
from src.infrastructure.postgres.models.user import FollowerModel, UserModel


class PostgresUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Mapping helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _to_entity(m: UserModel) -> User:
        return User(
            id=m.id,
            username=m.username,
            email=m.email,
            hashed_password=m.hashed_password,
            display_name=m.display_name,
            avatar_url=m.avatar_url,
            bio=m.bio,
            role=UserRole(m.role),
            reputation_score=m.reputation_score,
            accuracy_score=m.accuracy_score,
            total_predictions=m.total_predictions,
            resolved_predictions=m.resolved_predictions,
            virtual_points=m.virtual_points,
            is_active=m.is_active,
            is_verified=m.is_verified,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    # ── CRUD ──────────────────────────────────────────────────────────────────

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            role=user.role.value,
            reputation_score=user.reputation_score,
            accuracy_score=user.accuracy_score,
            total_predictions=user.total_predictions,
            resolved_predictions=user.resolved_predictions,
            virtual_points=user.virtual_points,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        repo = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        m = repo.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def get_by_email(self, email: str) -> Optional[User]:
        r = await self._session.execute(select(UserModel).where(UserModel.email == email))
        m = r.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def get_by_username(self, username: str) -> Optional[User]:
        r = await self._session.execute(select(UserModel).where(UserModel.username == username))
        m = r.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def update(self, user: User) -> User:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                username=user.username,
                email=user.email,
                display_name=user.display_name,
                avatar_url=user.avatar_url,
                bio=user.bio,
                role=user.role.value,
                reputation_score=user.reputation_score,
                accuracy_score=user.accuracy_score,
                total_predictions=user.total_predictions,
                resolved_predictions=user.resolved_predictions,
                virtual_points=user.virtual_points,
                is_active=user.is_active,
                is_verified=user.is_verified,
            )
        )
        await self._session.flush()
        return user

    async def delete(self, user_id: str) -> None:
        r = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        m = r.scalar_one_or_none()
        if m:
            await self._session.delete(m)
            await self._session.flush()

    # ── Search / Leaderboard ─────────────────────────────────────────────────

    async def search(self, query: str, skip: int = 0, limit: int = 20) -> List[User]:
        stmt = (
            select(UserModel)
            .where(
                UserModel.is_active.is_(True),
                or_(
                    UserModel.username.ilike(f"%{query}%"),
                    UserModel.display_name.ilike(f"%{query}%"),
                ),
            )
            .offset(skip)
            .limit(limit)
        )
        r = await self._session.execute(stmt)
        return [self._to_entity(m) for m in r.scalars().all()]

    async def get_leaderboard(
        self,
        skip: int = 0,
        limit: int = 20,
        category_slug: Optional[str] = None,
    ) -> List[User]:
        stmt = (
            select(UserModel)
            .where(UserModel.is_active.is_(True))
            .order_by(UserModel.reputation_score.desc())
            .offset(skip)
            .limit(limit)
        )
        r = await self._session.execute(stmt)
        return [self._to_entity(m) for m in r.scalars().all()]

    # ── Follow system ─────────────────────────────────────────────────────────

    async def follow(self, follower_id: str, following_id: str) -> None:
        self._session.add(FollowerModel(follower_id=follower_id, following_id=following_id))
        await self._session.flush()

    async def unfollow(self, follower_id: str, following_id: str) -> None:
        r = await self._session.execute(
            select(FollowerModel).where(
                FollowerModel.follower_id == follower_id,
                FollowerModel.following_id == following_id,
            )
        )
        row = r.scalar_one_or_none()
        if row:
            await self._session.delete(row)
            await self._session.flush()

    async def get_followers(self, user_id: str, skip: int = 0, limit: int = 20) -> List[User]:
        stmt = (
            select(UserModel)
            .join(FollowerModel, FollowerModel.follower_id == UserModel.id)
            .where(FollowerModel.following_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        r = await self._session.execute(stmt)
        return [self._to_entity(m) for m in r.scalars().all()]

    async def get_following(self, user_id: str, skip: int = 0, limit: int = 20) -> List[User]:
        stmt = (
            select(UserModel)
            .join(FollowerModel, FollowerModel.following_id == UserModel.id)
            .where(FollowerModel.follower_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        r = await self._session.execute(stmt)
        return [self._to_entity(m) for m in r.scalars().all()]

    async def is_following(self, follower_id: str, following_id: str) -> bool:
        r = await self._session.execute(
            select(FollowerModel).where(
                FollowerModel.follower_id == follower_id,
                FollowerModel.following_id == following_id,
            )
        )
        return r.scalar_one_or_none() is not None
