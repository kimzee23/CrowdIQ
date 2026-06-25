"""
CrowdIQ — Auth Service
Handles registration, login, token refresh, password reset.
"""
from __future__ import annotations

from src.application.port.input.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from src.domain.model.user import User
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import ConflictError, NotFoundError, UnauthorizedError
from src.infrastructure.config.security.jwt import create_access_token, create_refresh_token, decode_token
from src.infrastructure.config.security.password import hash_password, verify_password
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now


class AuthService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def register(self, req: RegisterRequest) -> TokenResponse:
        if await self._users.get_by_email(req.email):
            raise ConflictError("Email already registered")
        if await self._users.get_by_username(req.username):
            raise ConflictError("Username already taken")

        user = User(
            id=generate_uuid(),
            username=req.username,
            email=req.email,
            hashed_password=hash_password(req.password),
            display_name=req.display_name or req.username,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        print("created_at:", user.created_at)
        print("updated_at:", user.updated_at)
        print("tzinfo:", user.created_at.tzinfo)
        user = await self._users.create(user)
        return self._issue_tokens(user)

    async def login(self, req: LoginRequest) -> TokenResponse:
        user = await self._users.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is suspended")
        return self._issue_tokens(user)

    async def refresh(self, req: RefreshRequest) -> TokenResponse:
        payload = decode_token(req.refresh_token, expected_type="refresh")
        user = await self._users.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")
        return self._issue_tokens(user)

    async def me(self, user_id: str) -> User:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user

    async def forgot_password(self, req: ForgotPasswordRequest) -> dict:
        # In production: generate a signed token, store it in Redis with TTL,
        # and send via Celery email task. Returning a stub here.
        user = await self._users.get_by_email(req.email)
        if user:
            reset_token = create_access_token(subject=user.id, extra={"purpose": "reset"})
            # tasks.send_email_notification.delay(...)
            return {"reset_token": reset_token}  # dev only — never expose in prod
        return {"message": "If the email exists, a reset link has been sent"}

    async def reset_password(self, req: ResetPasswordRequest) -> dict:
        payload = decode_token(req.token, expected_type="access")
        if payload.get("purpose") != "reset":
            raise UnauthorizedError("Invalid reset token")
        user = await self._users.get_by_id(payload["sub"])
        if not user:
            raise NotFoundError("User", payload["sub"])
        user.hashed_password = hash_password(req.new_password)
        user.updated_at = utc_now()
        await self._users.update(user)
        return {"message": "Password reset successfully"}

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _issue_tokens(user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(
                subject=user.id, extra={"role": user.role.value}
            ),
            refresh_token=create_refresh_token(subject=user.id),
        )
