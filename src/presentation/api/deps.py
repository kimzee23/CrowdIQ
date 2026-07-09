"""
CrowdIQ — FastAPI Dependency Injection
Resolves repositories → services for every request.
"""
from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.service.ai import AIService
from src.domain.service.user import UserService
from src.domain.service.comment import CommentService
from src.domain.service.notification import NotificationService
from src.domain.service.prediction import PredictionService
from src.domain.service.search import SearchService
from src.domain.service.vote import VoteService
from src.domain.service.wallet import WalletService
from src.domain.model.user import User
from src.infrastructure.persistence.repository.database import get_db
from src.infrastructure.persistence.repositories.comment_repo import PostgresCommentRepository
from src.infrastructure.persistence.repositories.notification_repo import PostgresNotificationRepository
from src.infrastructure.persistence.repositories.prediction_repo import (
    PostgresCategoryRepository,
    PostgresPredictionRepository,
)
from src.infrastructure.persistence.repositories.reputation_repo import (
    PostgresReputationRepository,
    PostgresWalletRepository,
)
from src.infrastructure.persistence.repositories.user_repo import PostgresUserRepository
from src.infrastructure.persistence.repositories.vote_repo import PostgresVoteRepository
from src.domain.exception.base import UnauthorizedError
from src.infrastructure.security.jwt import decode_token

# ── Split auth / otp services ──────────────────────────────────────────────────
from src.domain.service.auth.login import LoginService
from src.domain.service.auth.register import RegisterService
from src.domain.service.auth.refresh_token import RefreshTokenService
from src.domain.service.auth.me import MeService
from src.domain.service.auth.forgot_password import ForgotPasswordService
from src.domain.service.auth.verify_reset_otp import VerifyResetOTPService
from src.domain.service.auth.reset_password import ResetPasswordService
from src.domain.service.otp.send_otp import SendOTPService
from src.domain.service.otp.verify_otp import VerifyOTPService

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

def get_login_service(repo: PostgresUserRepository = Depends(get_user_repo)) -> LoginService:
    return LoginService(repo)

def get_register_service(repo: PostgresUserRepository = Depends(get_user_repo)) -> RegisterService:
    return RegisterService(repo)

def get_refresh_token_service(repo: PostgresUserRepository = Depends(get_user_repo)) -> RefreshTokenService:
    return RefreshTokenService(repo)

def get_me_service(repo: PostgresUserRepository = Depends(get_user_repo)) -> MeService:
    return MeService(repo)

def get_forgot_password_service(repo: PostgresUserRepository = Depends(get_user_repo)) -> ForgotPasswordService:
    return ForgotPasswordService(repo)

def get_verify_reset_otp_service(repo: PostgresUserRepository = Depends(get_user_repo)) -> VerifyResetOTPService:
    return VerifyResetOTPService(repo)

def get_reset_password_service(repo: PostgresUserRepository = Depends(get_user_repo)) -> ResetPasswordService:
    return ResetPasswordService(repo)

def get_send_otp_service(repo: PostgresUserRepository = Depends(get_user_repo)) -> SendOTPService:
    return SendOTPService(repo)

def get_verify_otp_service(repo: PostgresUserRepository = Depends(get_user_repo)) -> VerifyOTPService:
    return VerifyOTPService(repo)

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