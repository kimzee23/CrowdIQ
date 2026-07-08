"""
CrowdIQ — Auth DTOs
"""
from __future__ import annotations

import re

from pydantic import BaseModel, EmailStr, Field, field_validator


_PASSWORD_RE = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':",.<>?/\\|`~]).{8,128}$'
)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str | None = Field(None, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not _PASSWORD_RE.match(v):
            raise ValueError(
                "Password must be 8-128 characters and contain at least one "
                "uppercase letter, one lowercase letter, one digit, and one "
                "special character (!@#$%^&* etc.)"
            )
        return v


class RegisterResponse(BaseModel):
    message: str
    email: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not _PASSWORD_RE.match(v):
            raise ValueError(
                "Password must be 8-128 characters and contain at least one "
                "uppercase letter, one lowercase letter, one digit, and one "
                "special character."
            )
        return v


# ── OTP / Email Verification ──────────────────────────────────────────────────

class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


# ── Password Reset (OTP-verified) ─────────────────────────────────────────────

class VerifyResetOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class ResetTokenResponse(BaseModel):
    """Short-lived token used exclusively for submitting a new password."""
    reset_token: str
    message: str = "OTP verified. Use the reset_token to set a new password."
