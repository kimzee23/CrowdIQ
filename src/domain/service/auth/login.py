"""
CrowdIQ — Login Service
Authenticates a user by email/password and issues JWT tokens.
"""
from __future__ import annotations

from application.validator.login_validator import LoginValidator
from src.application.dto.auth import LoginRequest, TokenResponse
from src.application.port.output.user_repository import AbstractUserRepository
from src.domain.exception.base import UnauthorizedError
from src.domain.service.token.token_service import TokenService
from src.infrastructure.security.password import verify_password


class LoginService:
    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._users = user_repo

    async def __call__(self, req: LoginRequest) -> TokenResponse:
        user = await self._users.get_by_email(req.email)

        if user is None or not verify_password(req.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        LoginValidator.validate_login_request(user)

        return TokenService.issue_tokens(user)
