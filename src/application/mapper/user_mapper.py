"""
CrowdIQ — User Mapper
"""
from src.application.dto.user import UserResponse, UserPublicResponse
from src.domain.model.user import User


def to_user_response(u: User) -> UserResponse:
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
