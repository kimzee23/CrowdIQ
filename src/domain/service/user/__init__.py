"""
CrowdIQ — User Service Package
"""
from __future__ import annotations

from src.domain.service.user.update_profile import UpdateProfile
from src.domain.service.user.follow_user import FollowUser
from src.domain.service.user.unfollow_user import UnfollowUser

__all__ = ["UpdateProfile", "FollowUser", "UnfollowUser"]

from .auth_service import AuthService
from .user_service import UserService
__all__.extend(['AuthService', 'UserService'])
