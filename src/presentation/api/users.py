"""
CrowdIQ — Users Router  /api/v1/users
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from src.application.dto.user import (
    UpdateUserRequest,
    UserPublicResponse,
    UserResponse,
)
from src.domain.service.user import UserService
from src.domain.model.user import User
from src.presentation.api.deps import get_current_user, get_user_service
from src.infrastructure.config.utils.helpers import paginate
from src.application.mapper.user_mapper import to_user_public_response, to_user_response

router = APIRouter(prefix="/users", tags=["Users"])




@router.get("/search", response_model=list[UserPublicResponse])
async def search_users(
    q: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 20,
    svc: UserService = Depends(get_user_service),
):
    sk, lm = paginate(skip, limit)
    users = await svc.search_users(q, sk, lm)
    return [to_user_public_response(u) for u in users]


@router.get("/leaderboard", response_model=list[UserPublicResponse])
async def leaderboard(
    skip: int = 0,
    limit: int = 20,
    category: str | None = None,
    svc: UserService = Depends(get_user_service),
):
    sk, lm = paginate(skip, limit)
    users = await svc.get_leaderboard(sk, lm, category)
    return [to_user_public_response(u) for u in users]


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user(user_id: str, svc: UserService = Depends(get_user_service)):
    return to_user_public_response(await svc.get_user(user_id))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    req: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
):
    return to_user_response(await svc.update_user(user_id, req, current_user.id))


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
    return [to_user_public_response(u) for u in users]


@router.get("/{user_id}/following", response_model=list[UserPublicResponse])
async def get_following(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    svc: UserService = Depends(get_user_service),
):
    sk, lm = paginate(skip, limit)
    users = await svc.get_following(user_id, sk, lm)
    return [to_user_public_response(u) for u in users]


@router.get("/{user_id}/votes")
async def get_user_votes(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
):
    return {"user_id": user_id, "message": "Use /api/v1/users/{id}/votes via vote router"}
