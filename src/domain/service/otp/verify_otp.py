"""
CrowdIQ — Verify OTP Service
Validates a submitted OTP and marks the user's email as verified.
"""
from __future__ import annotations

from src.application.dto.auth import VerifyOTPRequest
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import NotFoundError, DomainValidationError
from src.domain.service.otp.otp_service import OTPService
from src.infrastructure.config.utils.helpers import utc_now

OTP_PREFIX = "otp"


class VerifyOTPService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def __call__(self, req: VerifyOTPRequest) -> dict:
        user = await self._users.get_by_email(req.email)
        if not user:
            raise NotFoundError("User", req.email)

        is_valid = await OTPService.validate(OTP_PREFIX, req.email, req.otp)
        if not is_valid:
            raise DomainValidationError("Invalid or expired OTP")

        user.is_verified = True
        user.updated_at = utc_now()
        await self._users.update(user)

        return {"message": "Email verified successfully"}
