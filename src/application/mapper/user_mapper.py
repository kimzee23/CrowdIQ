"""
CrowdIQ — User Mapper
"""
from src.application.dto.user import UserResponse, UserPublicResponse
from src.domain.model.user import User


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        role=user.role.value,
        reputation_score=user.reputation_score,
        accuracy_score=user.accuracy_score,
        total_predictions=user.total_predictions,
        resolved_predictions=user.resolved_predictions,
        virtual_points=user.virtual_points,
        reputation_level=user.reputation_level.value,
        win_rate=user.win_rate,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )


def to_user_public_response(u: User) -> UserPublicResponse:
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
