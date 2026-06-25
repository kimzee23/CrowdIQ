"""
CrowdIQ — Redis Client
"""
from __future__ import annotations

import json
from typing import Any, Optional

import redis.asyncio as aioredis

from src.infrastructure.config.settings import settings

_redis: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    r = get_redis()
    await r.set(key, json.dumps(value), ex=ttl)


async def cache_get(key: str) -> Optional[Any]:
    r = get_redis()
    raw = await r.get(key)
    return json.loads(raw) if raw else None


async def cache_delete(key: str) -> None:
    r = get_redis()
    await r.delete(key)


async def cache_delete_pattern(pattern: str) -> None:
    r = get_redis()
    keys = await r.keys(pattern)
    if keys:
        await r.delete(*keys)
