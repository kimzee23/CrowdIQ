"""
CrowdIQ — Password Validator
"""
import re

from src.domain.exception.base import CrowdIQException


class ValidationError(CrowdIQException):
    def __init__(self, message: str):
        super().__init__(status_code=400, message=message)


def validate_password_strength(password: str) -> None:
    """
    Validates that a password meets minimum strength requirements.
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one digit.")
