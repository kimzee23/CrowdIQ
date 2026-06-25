"""
CrowdIQ — Users Router  /api/v1/users
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from src.application.port.input.user import (
    UpdateUserRequest,
    UserPublicResponse,
    UserResponse,
)
from src.domain.service.user_service import UserService
from src.domain.model.user import User
from src.infrastructure.input.rest.controller.deps import get_current_user, get_user_service
from src.infrastructure.config.utils.helpers import paginate

router = APIRouter(prefix="/users", tags=["Users"])


def _pub(u: User) -> UserPublicResponse:
    return UserPublicResponse(
        id=u.id,
        username=u.username,
        display_name=u.display_name,
        avatar_url=u.avatar_url,
        bio=u.bio,
        reputation_score=u.reputation_score,
        reputation_level=u.reputation_level.value,
        total_predictions=u.total_predictions,
        win_rate=u.win_rate,
        created_at=u.created_at,
    )


def _full(u: User) -> UserResponse:
    return UserResponse(
        id=u.id, username=u.username, email=u.email,
        display_name=u.display_name, avatar_url=u.avatar_url, bio=u.bio,
        role=u.role.value, reputation_score=u.reputation_score,
        accuracy_score=u.accuracy_score, total_predictions=u.total_predictions,
        resolved_predictions=u.resolved_predictions, virtual_points=u.virtual_points,
        reputation_level=u.reputation_level.value, win_rate=u.win_rate,
        is_active=u.is_active, is_verified=u.is_verified, created_at=u.created_at,
    )


@router.get("/search", response_model=list[UserPublicResponse])
async def search_users(
    q: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 20,
    svc: UserService = Depends(get_user_service),
):
    sk, lm = paginate(skip, limit)
    users = await svc.search_users(q, sk, lm)
    return [_pub(u) for u in users]


@router.get("/leaderboard", response_model=list[UserPublicResponse])
async def leaderboard(
    skip: int = 0,
    limit: int = 20,
    category: str | None = None,
    svc: UserService = Depends(get_user_service),
):
    sk, lm = paginate(skip, limit)
    users = await svc.get_leaderboard(sk, lm, category)
    return [_pub(u) for u in users]


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user(user_id: str, svc: UserService = Depends(get_user_service)):
    return _pub(await svc.get_user(user_id))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    req: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
):
    return _full(await svc.update_user(user_id, req, current_user.id))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
):
    await svc.delete_user(user_id, current_user)


# ── Follow system ─────────────────────────────────────────────────────────────

@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow(
    user_id: str,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
):
    await svc.follow(current_user.id, user_id)


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow(
    user_id: str,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
):
    await svc.unfollow(current_user.id, user_id)


@router.get("/{user_id}/followers", response_model=list[UserPublicResponse])
async def get_followers(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    svc: UserService = Depends(get_user_service),
):
    sk, lm = paginate(skip, limit)
    users = await svc.get_followers(user_id, sk, lm)
    return [_pub(u) for u in users]


@router.get("/{user_id}/following", response_model=list[UserPublicResponse])
async def get_following(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    svc: UserService = Depends(get_user_service),
):
    sk, lm = paginate(skip, limit)
    users = await svc.get_following(user_id, sk, lm)
    return [_pub(u) for u in users]


@router.get("/{user_id}/votes")
async def get_user_votes(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
):
    return {"user_id": user_id, "message": "Use /api/v1/users/{id}/votes via vote router"}
