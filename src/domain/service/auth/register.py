"""
CrowdIQ — Register Service
Creates a new user account and triggers email verification OTP.
"""
from __future__ import annotations

from src.application.dto.auth import RegisterRequest, RegisterResponse, SendOTPRequest
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import ConflictError
from src.domain.model.user import User
from src.domain.service.otp.send_otp import SendOTPService
from src.infrastructure.config.utils.helpers import generate_uuid, utc_now
from src.infrastructure.security.password import hash_password


class RegisterService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo
        self._send_otp = SendOTPService(user_repo)

    async def __call__(self, req: RegisterRequest) -> RegisterResponse:
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
        await self._send_otp(SendOTPRequest(email=user.email))

        return RegisterResponse(
            message="Account created. Please check your email for your OTP to verify your account.",
            email=user.email,
        )
