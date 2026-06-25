"""
CrowdIQ — FastAPI Dependency Injection
Resolves repositories → services for every request.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.service.ai_service import AIService
from src.domain.service.auth_service import AuthService
from src.domain.service.comment_service import CommentService
from src.domain.service.notification_service import NotificationService
from src.domain.service.prediction_service import PredictionService
from src.domain.service.search_service import SearchService
from src.domain.service.user_service import UserService
from src.domain.service.vote_service import VoteService
from src.domain.service.wallet_service import WalletService
from src.domain.model.user import User
from src.infrastructure.persistence.repository.database import get_db
from src.infrastructure.persistence.adapter.comment_repo import PostgresCommentRepository
from src.infrastructure.persistence.adapter.notification_repo import PostgresNotificationRepository
from src.infrastructure.persistence.adapter.prediction_repo import (
    PostgresCategoryRepository,
    PostgresPredictionRepository,
)
from src.infrastructure.persistence.adapter.reputation_repo import (
    PostgresReputationRepository,
    PostgresWalletRepository,
)
from src.infrastructure.persistence.adapter.user_repo import PostgresUserRepository
from src.infrastructure.persistence.adapter.vote_repo import PostgresVoteRepository
from src.domain.exception.base import UnauthorizedError
from src.infrastructure.config.security.jwt import decode_token

# ── Repository factories ──────────────────────────────────────────────────────

def get_user_repo(db: AsyncSession = Depends(get_db)) -> PostgresUserRepository:
    return PostgresUserRepository(db)

def get_prediction_repo(db: AsyncSession = Depends(get_db)) -> PostgresPredictionRepository:
    return PostgresPredictionRepository(db)

def get_category_repo(db: AsyncSession = Depends(get_db)) -> PostgresCategoryRepository:
    return PostgresCategoryRepository(db)

def get_vote_repo(db: AsyncSession = Depends(get_db)) -> PostgresVoteRepository:
    return PostgresVoteRepository(db)

def get_comment_repo(db: AsyncSession = Depends(get_db)) -> PostgresCommentRepository:
    return PostgresCommentRepository(db)

def get_notification_repo(db: AsyncSession = Depends(get_db)) -> PostgresNotificationRepository:
    return PostgresNotificationRepository(db)

def get_wallet_repo(db: AsyncSession = Depends(get_db)) -> PostgresWalletRepository:
    return PostgresWalletRepository(db)

def get_reputation_repo(db: AsyncSession = Depends(get_db)) -> PostgresReputationRepository:
    return PostgresReputationRepository(db)

# ── Service factories ─────────────────────────────────────────────────────────

def get_auth_service(repo=Depends(get_user_repo)) -> AuthService:
    return AuthService(repo)

def get_user_service(repo=Depends(get_user_repo)) -> UserService:
    return UserService(repo)

def get_prediction_service(
    pred_repo=Depends(get_prediction_repo),
    cat_repo=Depends(get_category_repo),
) -> PredictionService:
    return PredictionService(pred_repo, cat_repo)

def get_vote_service(
    vote_repo=Depends(get_vote_repo),
    pred_repo=Depends(get_prediction_repo),
    user_repo=Depends(get_user_repo),
    wallet_repo=Depends(get_wallet_repo),
) -> VoteService:
    return VoteService(vote_repo, pred_repo, user_repo, wallet_repo)

def get_comment_service(
    comment_repo=Depends(get_comment_repo),
    pred_repo=Depends(get_prediction_repo),
) -> CommentService:
    return CommentService(comment_repo, pred_repo)

def get_notification_service(repo=Depends(get_notification_repo)) -> NotificationService:
    return NotificationService(repo)

def get_wallet_service(repo=Depends(get_wallet_repo)) -> WalletService:
    return WalletService(repo)

def get_search_service(
    user_repo=Depends(get_user_repo),
    pred_repo=Depends(get_prediction_repo),
) -> SearchService:
    return SearchService(user_repo, pred_repo)

def get_ai_service() -> AIService:
    return AIService()

# ── Auth dependencies ─────────────────────────────────────────────────────────

security = HTTPBearer(auto_error=False)

async def _extract_user(
    token: str | None,
    user_repo: PostgresUserRepository,
    required: bool,
) -> User | None:
    if not token:
        if required:
            raise UnauthorizedError("Missing Authorization header")
        return None
    payload = decode_token(token, expected_type="access")
    user = await user_repo.get_by_id(payload["sub"])
    if not user:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise UnauthorizedError("Account is inactive")
    return user


async def get_current_user(
    auth: HTTPAuthorizationCredentials | None = Depends(security),
    user_repo: PostgresUserRepository = Depends(get_user_repo),
) -> User:
    token = auth.credentials if auth else None
    user = await _extract_user(token, user_repo, required=True)
    return user  # type: ignore[return-value]


async def get_optional_user(
    auth: HTTPAuthorizationCredentials | None = Depends(security),
    user_repo: PostgresUserRepository = Depends(get_user_repo),
) -> User | None:
    token = auth.credentials if auth else None
    return await _extract_user(token, user_repo, required=False)


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin():
        raise UnauthorizedError("Admin access required")
    return current_user


async def require_moderator(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_moderator_or_above():
        raise UnauthorizedError("Moderator access required")
    return current_user
