"""
CrowdIQ — Token Service
Handles JWT access/refresh token creation, decoding, and issuance.
"""
from __future__ import annotations

from src.domain.model.user import User
from src.application.dto.auth import TokenResponse
from src.infrastructure.security.jwt import create_access_token, create_refresh_token, decode_token


class TokenService:
    """Centralized JWT token operations."""

    @staticmethod
    def issue_tokens(user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(
                subject=user.id, extra={"role": user.role.value}
            ),
            refresh_token=create_refresh_token(subject=user.id),
        )

    @staticmethod
    def create_reset_token(user_id: str) -> str:
        return create_access_token(subject=user_id, extra={"purpose": "reset"})

    @staticmethod
    def decode(token: str, expected_type: str = "access") -> dict:
        return decode_token(token, expected_type=expected_type)

    @staticmethod
    def decode_refresh(token: str) -> dict:
        return decode_token(token, expected_type="refresh")
