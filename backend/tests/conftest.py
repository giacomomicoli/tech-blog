import pytest
import fakeredis.aioredis

import src.cache as cache_mod


@pytest.fixture(autouse=True)
async def fake_redis(monkeypatch):
    """Replace the real Redis connection with fakeredis for all tests.

    For sync test functions (e.g. those using TestClient), a new fakeredis
    instance is created per test so there's no event-loop cross-contamination.
    The monkeypatch ensures cache_mod always gets a fresh connection.
    """
    # Force a new redis connection per test by resetting the module-level singleton
    monkeypatch.setattr(cache_mod, "_redis", None)

    # Patch get_redis to return a per-call fakeredis bound to the current loop
    _instances: list[fakeredis.aioredis.FakeRedis] = []

    original_get_redis = cache_mod.get_redis

    async def _fake_get_redis():
        if cache_mod._redis is None:
            fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
            cache_mod._redis = fake
            _instances.append(fake)
        return cache_mod._redis

    monkeypatch.setattr(cache_mod, "get_redis", _fake_get_redis)
    yield

    for inst in _instances:
        try:
            await inst.flushall()
            await inst.aclose()
        except Exception:
            pass
    monkeypatch.setattr(cache_mod, "_redis", None)
