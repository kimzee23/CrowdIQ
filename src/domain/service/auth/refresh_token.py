"""
CrowdIQ — Refresh Token Service
Validates a refresh token and issues a new token pair.
"""
from __future__ import annotations

from src.application.dto.auth import RefreshRequest, TokenResponse
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import UnauthorizedError
from src.domain.service.token.token_service import TokenService


class RefreshTokenService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def __call__(self, req: RefreshRequest) -> TokenResponse:
        payload = TokenService.decode_refresh(req.refresh_token)
        user = await self._users.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")
        return TokenService.issue_tokens(user)
