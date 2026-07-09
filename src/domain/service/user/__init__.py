"""
CrowdIQ — User Service Package
"""
from __future__ import annotations

from src.domain.service.user.update_profile import UpdateProfile
from src.domain.service.user.follow_user import FollowUser
from src.domain.service.user.unfollow_user import UnfollowUser

__all__ = ["UpdateProfile", "FollowUser", "UnfollowUser"]

from .user_service import UserService
__all__.append("UserService")

# AuthService has been split into src.domain.service.auth.* and
# src.domain.service.otp.* — import from there instead, e.g.:
#   from src.domain.service.auth.login import LoginService
#   from src.domain.service.otp.send_otp import SendOTPService