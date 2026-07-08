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
from src.domain.service.user import AuthService
from src.domain.model.user import User
from src.presentation.api.deps import get_auth_service, get_current_user
from src.application.dto.user import UserResponse
from src.application.mapper.user_mapper import to_user_response

router = APIRouter(prefix="/auth", tags=["Auth"])





@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, svc: AuthService = Depends(get_auth_service)):
    return await svc.register(req)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, svc: AuthService = Depends(get_auth_service)):
    return await svc.login(req)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(_: User = Depends(get_current_user)):
    """Client-side token disposal. Server-side token blacklisting via Redis can be added here."""
    return None


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, svc: AuthService = Depends(get_auth_service)):
    return await svc.refresh(req)


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, svc: AuthService = Depends(get_auth_service)):
    """Step 1 — sends a 6-digit OTP to the user's email to confirm account ownership."""
    return await svc.forgot_password(req)


@router.post("/verify-reset-otp", response_model=ResetTokenResponse)
async def verify_reset_otp(req: VerifyResetOTPRequest, svc: AuthService = Depends(get_auth_service)):
    """Step 2 — validates the reset OTP and returns a short-lived reset token."""
    return await svc.verify_reset_otp(req)


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, svc: AuthService = Depends(get_auth_service)):
    """Step 3 — submits the reset token with a new password."""
    return await svc.reset_password(req)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return to_user_response(current_user)


@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(req: SendOTPRequest, svc: AuthService = Depends(get_auth_service)):
    return await svc.send_otp(req)


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(req: VerifyOTPRequest, svc: AuthService = Depends(get_auth_service)):
    return await svc.verify_otp(req)
