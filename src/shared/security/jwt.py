"""
CrowdIQ — JWT Utilities
Creates and decodes access / refresh tokens using python-jose.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from src.shared.configs.settings import settings
from src.shared.exceptions.base import UnauthorizedError


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    """Return a short-lived JWT access token."""
    payload: dict[str, Any] = {
        "sub": subject,
        "type": "access",
        "exp": _utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": _utc_now(),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Return a long-lived JWT refresh token."""
    payload: dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "exp": _utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": _utc_now(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """Decode and validate a JWT token, raising UnauthorizedError on failure."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    if payload.get("type") != expected_type:
        raise UnauthorizedError(f"Expected a '{expected_type}' token")

    return payload
