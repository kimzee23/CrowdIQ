"""
CrowdIQ — Reset Password Service
Step 3: Validates the reset token and sets a new password.
"""
from __future__ import annotations

from src.application.dto.auth import ResetPasswordRequest
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import NotFoundError, UnauthorizedError
from src.domain.service.token.token_service import TokenService
from src.infrastructure.config.utils.helpers import utc_now
from src.infrastructure.security.password import hash_password


class ResetPasswordService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def __call__(self, req: ResetPasswordRequest) -> dict:
        payload = TokenService.decode(req.token, expected_type="access")
        if payload.get("purpose") != "reset":
            raise UnauthorizedError("Invalid reset token")

        user = await self._users.get_by_id(payload["sub"])
        if not user:
            raise NotFoundError("User", payload["sub"])

        user.hashed_password = hash_password(req.new_password)
        user.updated_at = utc_now()
        await self._users.update(user)

        return {"message": "Password reset successfully"}
