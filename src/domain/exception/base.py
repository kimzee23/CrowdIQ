"""
CrowdIQ — Domain / Application Exceptions
All custom exceptions used throughout the application are defined here.
"""
from __future__ import annotations

from fastapi import status


class CrowdIQException(Exception):
    """Base exception carrying an HTTP status code and a human-readable message."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# ── 404 ──────────────────────────────────────────────────────────────────────

class NotFoundError(CrowdIQException):
    def __init__(self, resource: str, identifier: str | int = "") -> None:
        msg = (
            f"{resource} not found"
            if not identifier
            else f"{resource} '{identifier}' not found"
        )
        super().__init__(msg, status.HTTP_404_NOT_FOUND)


# ── 401 / 403 ─────────────────────────────────────────────────────────────────

class UnauthorizedError(CrowdIQException):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(CrowdIQException):
    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN)


# ── 409 ───────────────────────────────────────────────────────────────────────

class ConflictError(CrowdIQException):
    def __init__(self, message: str) -> None:
        super().__init__(message, status.HTTP_409_CONFLICT)


# ── 422 ───────────────────────────────────────────────────────────────────────

class DomainValidationError(CrowdIQException):
    def __init__(self, message: str) -> None:
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


# ── 400 domain-specific ───────────────────────────────────────────────────────

class InsufficientPointsError(CrowdIQException):
    def __init__(self, required: int, available: int) -> None:
        super().__init__(
            f"Insufficient virtual points: need {required}, have {available}",
            status.HTTP_400_BAD_REQUEST,
        )


class PredictionStatusError(CrowdIQException):
    def __init__(self, action: str, current_status: str) -> None:
        super().__init__(
            f"Cannot '{action}' a prediction with status '{current_status}'",
            status.HTTP_400_BAD_REQUEST,
        )


class AlreadyVotedError(CrowdIQException):
    def __init__(self) -> None:
        super().__init__("You have already voted on this prediction", status.HTTP_409_CONFLICT)


class SelfFollowError(CrowdIQException):
    def __init__(self) -> None:
        super().__init__("You cannot follow yourself", status.HTTP_400_BAD_REQUEST)
