"""
CrowdIQ — OTP Service
Core OTP generation, storage, and validation logic (cache-backed).
"""
from __future__ import annotations

import random

from src.infrastructure.cache.client import cache_set, cache_get, cache_delete

OTP_LENGTH = 6
OTP_TTL_SECONDS = 300


class OTPService:
    """Low-level OTP generate/store/verify operations."""

    @staticmethod
    def generate() -> str:
        return "".join(random.choices("0123456789", k=OTP_LENGTH))

    @staticmethod
    def _key(prefix: str, email: str) -> str:
        return f"{prefix}:{email}"

    @classmethod
    async def store(cls, prefix: str, email: str, otp: str, ttl: int = OTP_TTL_SECONDS) -> None:
        await cache_set(cls._key(prefix, email), otp, ttl=ttl)

    @classmethod
    async def get(cls, prefix: str, email: str) -> str | None:
        return await cache_get(cls._key(prefix, email))

    @classmethod
    async def consume(cls, prefix: str, email: str) -> None:
        await cache_delete(cls._key(prefix, email))

    @classmethod
    async def validate(cls, prefix: str, email: str, otp: str) -> bool:
        cached_otp = await cls.get(prefix, email)
        if not cached_otp or cached_otp != otp:
            return False
        await cls.consume(prefix, email)
        return True
