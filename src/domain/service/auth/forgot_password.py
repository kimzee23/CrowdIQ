"""
CrowdIQ — Forgot Password Service
Step 1: Verifies account ownership by sending a reset OTP.
"""
from __future__ import annotations

from src.application.dto.auth import ForgotPasswordRequest
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.service.otp.send_otp import SendOTPService


class ForgotPasswordService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo
        self._send_otp = SendOTPService(user_repo)

    async def __call__(self, req: ForgotPasswordRequest) -> dict:
        user = await self._users.get_by_email(req.email)
        # Always return success message to avoid email enumeration
        if not user:
            return {"message": "If that email exists, a reset OTP has been sent."}

        return await self._send_otp.send_reset_otp(req.email)
