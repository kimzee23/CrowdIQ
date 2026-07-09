"""
CrowdIQ — Auth Router  /api/v1/auth
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.application.dto.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetTokenResponse,
    TokenResponse,
    SendOTPRequest,
    VerifyOTPRequest,
    VerifyResetOTPRequest,
)
from src.domain.model.user import User
from src.domain.service.auth.login import LoginService
from src.domain.service.auth.register import RegisterService
from src.domain.service.auth.refresh_token import RefreshTokenService
from src.domain.service.auth.forgot_password import ForgotPasswordService
from src.domain.service.auth.verify_reset_otp import VerifyResetOTPService
from src.domain.service.auth.reset_password import ResetPasswordService
from src.domain.service.otp.send_otp import SendOTPService
from src.domain.service.otp.verify_otp import VerifyOTPService
from src.presentation.api.deps import (
    get_current_user,
    get_login_service,
    get_register_service,
    get_refresh_token_service,
    get_forgot_password_service,
    get_verify_reset_otp_service,
    get_reset_password_service,
    get_send_otp_service,
    get_verify_otp_service,
)
from src.application.dto.user import UserResponse
from src.application.mapper.user_mapper import to_user_response

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, svc: RegisterService = Depends(get_register_service)):
    return await svc(req)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, svc: LoginService = Depends(get_login_service)):
    return await svc(req)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(_: User = Depends(get_current_user)):
    """Client-side token disposal. Server-side token blacklisting via Redis can be added here."""
    return None


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, svc: RefreshTokenService = Depends(get_refresh_token_service)):
    return await svc(req)


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, svc: ForgotPasswordService = Depends(get_forgot_password_service)):
    """Step 1 — sends a 6-digit OTP to the user's email to confirm account ownership."""
    return await svc(req)


@router.post("/verify-reset-otp", response_model=ResetTokenResponse)
async def verify_reset_otp(req: VerifyResetOTPRequest, svc: VerifyResetOTPService = Depends(get_verify_reset_otp_service)):
    """Step 2 — validates the reset OTP and returns a short-lived reset token."""
    return await svc(req)


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, svc: ResetPasswordService = Depends(get_reset_password_service)):
    """Step 3 — submits the reset token with a new password."""
    return await svc(req)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return to_user_response(current_user)


@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(req: SendOTPRequest, svc: SendOTPService = Depends(get_send_otp_service)):
    return await svc(req)


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(req: VerifyOTPRequest, svc: VerifyOTPService = Depends(get_verify_otp_service)):
    return await svc(req)