"""
CrowdIQ — Auth Router  /api/v1/auth
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.application.port.input.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from src.domain.service.auth_service import AuthService
from src.domain.model.user import User
from src.infrastructure.input.rest.controller.deps import get_auth_service, get_current_user
from src.application.port.input.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


def _user_to_response(u: User) -> UserResponse:
    return UserResponse(
        id=u.id,
        username=u.username,
        email=u.email,
        display_name=u.display_name,
        avatar_url=u.avatar_url,
        bio=u.bio,
        role=u.role.value,
        reputation_score=u.reputation_score,
        accuracy_score=u.accuracy_score,
        total_predictions=u.total_predictions,
        resolved_predictions=u.resolved_predictions,
        virtual_points=u.virtual_points,
        reputation_level=u.reputation_level.value,
        win_rate=u.win_rate,
        is_active=u.is_active,
        is_verified=u.is_verified,
        created_at=u.created_at,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
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
    return await svc.forgot_password(req)


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, svc: AuthService = Depends(get_auth_service)):
    return await svc.reset_password(req)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return _user_to_response(current_user)
