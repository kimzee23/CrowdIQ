"""
CrowdIQ — Send OTP Service
Generates and dispatches an OTP for a given purpose (verification or reset).
"""
from __future__ import annotations

from src.application.dto.auth import SendOTPRequest
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import NotFoundError
from src.domain.service.email.email_service import EmailService
from src.domain.service.otp.otp_service import OTPService

OTP_PREFIX = "otp"
RESET_OTP_PREFIX = "reset_otp"


class SendOTPService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def send_verification_otp(self, req: SendOTPRequest) -> dict:
        user = await self._users.get_by_email(req.email)
        if not user:
            raise NotFoundError("User", req.email)

        otp = OTPService.generate()
        await OTPService.store(OTP_PREFIX, req.email, otp)

        print(f"\n[OTP TERMINAL VERIFICATION] Email: {req.email} | OTP: {otp}\n")
        EmailService.send_otp_email(req.email, otp)
        print(f"[OTP SMS STUB] SMS OTP {otp} generated for {req.email}")

        return {"message": "OTP sent successfully"}

    async def send_reset_otp(self, email: str) -> dict:
        """Used by forgot-password flow. Does not raise on missing user."""
        otp = OTPService.generate()
        await OTPService.store(RESET_OTP_PREFIX, email, otp)

        print(f"\n[PASSWORD RESET OTP] Email: {email} | OTP: {otp}\n")
        EmailService.send_reset_otp_email(email, otp)
        print(f"[RESET OTP SMS STUB] OTP {otp} generated for {email}")

        return {"message": "If that email exists, a reset OTP has been sent."}

    # Backwards-compatible alias matching original AuthService.send_otp
    async def __call__(self, req: SendOTPRequest) -> dict:
        return await self.send_verification_otp(req)
