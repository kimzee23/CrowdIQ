"""
CrowdIQ — Auth Service
Handles registration, login, token refresh, password reset.
"""
from __future__ import annotations

from application.validator.login_validator import LoginValidator
from src.application.dto.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetTokenResponse,
    TokenResponse,
    SendOTPRequest,
    VerifyOTPRequest,
    VerifyResetOTPRequest,
)
from src.domain.model.user import User
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import ConflictError, NotFoundError, UnauthorizedError, DomainValidationError
from src.infrastructure.security.jwt import create_access_token, create_refresh_token, decode_token
from src.infrastructure.security.password import hash_password, verify_password
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now
import random
from src.infrastructure.cache.client import cache_set, cache_get, cache_delete
from src.infrastructure.celery.tasks import send_email_notification


class AuthService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def register(self, req: RegisterRequest) -> RegisterResponse:
        if await self._users.get_by_email(req.email):
            raise ConflictError("Email already registered")
        if await self._users.get_by_username(req.username):
            raise ConflictError("Username already taken")
        if req.display_name and await self._users.get_by_display_name(req.display_name):
            raise ConflictError("Display name already taken")

        user = User(
            id=generate_uuid(),
            username=req.username,
            email=req.email,
            hashed_password=hash_password(req.password),
            display_name=req.display_name or req.username,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        user = await self._users.create(user)

        # Auto-send OTP for email verification
        await self.send_otp(SendOTPRequest(email=user.email))

        return RegisterResponse(
            message="Account created. Please check your email for your OTP to verify your account.",
            email=user.email,
        )

    async def login(self, req: LoginRequest) -> TokenResponse:
        user = await self._users.get_by_email(req.email)

        if user is None or not verify_password(req.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        LoginValidator.validate_login_request(user)

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
        """Step 1: Verify account ownership by sending a reset OTP."""
        user = await self._users.get_by_email(req.email)
        # Always return success message to avoid email enumeration
        if not user:
            return {"message": "If that email exists, a reset OTP has been sent."}

        otp = "".join(random.choices("0123456789", k=6))
        await cache_set(f"reset_otp:{req.email}", otp, ttl=300)

        # 1. Print to terminal (local dev)
        print(f"\n[PASSWORD RESET OTP] Email: {req.email} | OTP: {otp}\n")

        # 2. Send via email (Celery task)
        send_email_notification.delay(
            to_email=req.email,
            subject="CrowdIQ Password Reset OTP",
            body=(
                f"You requested a password reset. Your OTP is: {otp}.\n"
                f"It is valid for 5 minutes. Do not share it with anyone."
            ),
        )

        # 3. SMS stub
        print(f"[RESET OTP SMS STUB] OTP {otp} generated for {req.email}")

        return {"message": "If that email exists, a reset OTP has been sent."}

    async def verify_reset_otp(self, req: VerifyResetOTPRequest) -> ResetTokenResponse:
        """Step 2: Validate the reset OTP and issue a short-lived reset JWT."""
        user = await self._users.get_by_email(req.email)
        if not user:
            raise NotFoundError("User", req.email)

        cached_otp = await cache_get(f"reset_otp:{req.email}")
        if not cached_otp or cached_otp != req.otp:
            raise DomainValidationError("Invalid or expired reset OTP")

        # Consume the OTP — single use only
        await cache_delete(f"reset_otp:{req.email}")

        reset_token = create_access_token(
            subject=user.id, extra={"purpose": "reset"}
        )
        return ResetTokenResponse(reset_token=reset_token)

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

    async def send_otp(self, req: SendOTPRequest) -> dict:
        user = await self._users.get_by_email(req.email)
        if not user:
            raise NotFoundError("User", req.email)

        otp = "".join(random.choices("0123456789", k=6))
        await cache_set(f"otp:{req.email}", otp, ttl=300)

        # 1. Print locally to terminal
        print(f"\n[OTP TERMINAL VERIFICATION] Email: {req.email} | OTP: {otp}\n")

        # 2. Send email via Celery background task
        send_email_notification.delay(
            to_email=req.email,
            subject="Your CrowdIQ OTP Code",
            body=f"Your OTP code is: {otp}. It is valid for 5 minutes."
        )

        # 3. Log stub for SMS
        print(f"[OTP SMS STUB] SMS OTP {otp} generated for {req.email}")

        return {"message": "OTP sent successfully"}

    async def verify_otp(self, req: VerifyOTPRequest) -> dict:
        user = await self._users.get_by_email(req.email)
        if not user:
            raise NotFoundError("User", req.email)

        cached_otp = await cache_get(f"otp:{req.email}")
        if not cached_otp or cached_otp != req.otp:
            raise DomainValidationError("Invalid or expired OTP")

        user.is_verified = True
        user.updated_at = utc_now()
        await self._users.update(user)
        await cache_delete(f"otp:{req.email}")

        return {"message": "Email verified successfully"}

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _issue_tokens(user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(
                subject=user.id, extra={"role": user.role.value}
            ),
            refresh_token=create_refresh_token(subject=user.id),
        )
