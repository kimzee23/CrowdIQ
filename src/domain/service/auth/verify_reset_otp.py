"""
CrowdIQ — Verify Reset OTP Service
Step 2: Validates the reset OTP and issues a short-lived reset JWT.
"""
from __future__ import annotations

from src.application.dto.auth import VerifyResetOTPRequest, ResetTokenResponse
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import NotFoundError, DomainValidationError
from src.domain.service.otp.otp_service import OTPService
from src.domain.service.token.token_service import TokenService

RESET_OTP_PREFIX = "reset_otp"


class VerifyResetOTPService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def __call__(self, req: VerifyResetOTPRequest) -> ResetTokenResponse:
        user = await self._users.get_by_email(req.email)
        if not user:
            raise NotFoundError("User", req.email)

        is_valid = await OTPService.validate(RESET_OTP_PREFIX, req.email, req.otp)
        if not is_valid:
            raise DomainValidationError("Invalid or expired reset OTP")

        reset_token = TokenService.create_reset_token(user.id)
        return ResetTokenResponse(reset_token=reset_token)
