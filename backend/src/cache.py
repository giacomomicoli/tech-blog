import json
from typing import Any

import redis.asyncio as aioredis

from src.config import settings

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def close_redis():
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


# ── Key helpers ─────────────────────────────────────────────

PREFIX = "blog"


def _key(*parts: str) -> str:
    return f"{PREFIX}:{':'.join(parts)}"


def posts_list_key(
    lang: str = "",
    tag: str | None = None,
    category: str | None = None,
    featured: bool | None = None,
    page: int = 1,
    limit: int = 10,
) -> str:
    suffix = f"tag:{tag}" if tag else f"cat:{category}" if category else "all"
    if featured is not None:
        suffix += f":featured:{featured}"
    return _key(lang, "posts", suffix, str(page), str(limit))


def post_key(lang: str, slug: str) -> str:
    return _key(lang, "posts", slug)


def page_key(lang: str, slug: str) -> str:
    return _key(lang, "page", slug)


def categories_key(lang: str = "") -> str:
    return _key(lang, "categories")


def tags_key(lang: str = "") -> str:
    return _key(lang, "tags")


def hero_key(lang: str = "") -> str:
    return _key(lang, "hero")


def top_key(lang: str = "") -> str:
    return _key(lang, "top")


# ── Cache operations ────────────────────────────────────────


async def cache_get(key: str) -> Any | None:
    r = await get_redis()
    raw = await r.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    r = await get_redis()
    ttl = ttl or settings.cache_ttl_seconds
    await r.set(key, json.dumps(value, default=str), ex=ttl)


async def cache_invalidate(pattern: str) -> int:
    """Delete all keys matching pattern. Returns count of deleted keys."""
    r = await get_redis()
    count = 0
    async for key in r.scan_iter(match=pattern):
        await r.delete(key)
        count += 1
    return count


async def cache_invalidate_all() -> int:
    """Flush all blog cache keys."""
    return await cache_invalidate(f"{PREFIX}:*")
