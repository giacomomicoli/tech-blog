"""Tests for the Redis cache layer."""

from src.cache import (
    cache_get,
    cache_invalidate,
    cache_invalidate_all,
    cache_set,
    categories_key,
    page_key,
    post_key,
    posts_list_key,
    tags_key,
)


# ── Key helpers ────────────────────────────────────────────


class TestKeyHelpers:
    def test_posts_list_key_default(self):
        assert posts_list_key(lang="it") == "blog:it:posts:all:1:10"

    def test_posts_list_key_with_tag(self):
        assert posts_list_key(lang="en", tag="python") == "blog:en:posts:tag:python:1:10"

    def test_posts_list_key_with_category(self):
        assert posts_list_key(lang="it", category="Tech") == "blog:it:posts:cat:Tech:1:10"

    def test_posts_list_key_with_page(self):
        assert posts_list_key(lang="it", page=3) == "blog:it:posts:all:3:10"

    def test_posts_list_key_with_limit(self):
        assert posts_list_key(lang="it", limit=50) == "blog:it:posts:all:1:50"

    def test_post_key(self):
        assert post_key("en", "my-slug") == "blog:en:posts:my-slug"

    def test_page_key(self):
        assert page_key("it", "about-blog") == "blog:it:page:about-blog"

    def test_categories_key(self):
        assert categories_key("it") == "blog:it:categories"

    def test_tags_key(self):
        assert tags_key("en") == "blog:en:tags"


# ── Cache operations ───────────────────────────────────────


class TestCacheOperations:
    async def test_set_and_get(self):
        await cache_set("blog:test", {"hello": "world"})
        result = await cache_get("blog:test")
        assert result == {"hello": "world"}

    async def test_get_missing_key(self):
        result = await cache_get("blog:nonexistent")
        assert result is None

    async def test_set_overwrites(self):
        await cache_set("blog:key", "first")
        await cache_set("blog:key", "second")
        assert await cache_get("blog:key") == "second"

    async def test_set_with_complex_data(self):
        data = {
            "posts": [{"id": "1", "title": "Test"}],
            "total": 1,
            "page": 1,
            "has_more": False,
        }
        await cache_set("blog:complex", data)
        result = await cache_get("blog:complex")
        assert result == data

    async def test_invalidate_pattern(self):
        await cache_set("blog:posts:all:1", "a")
        await cache_set("blog:posts:all:2", "b")
        await cache_set("blog:categories", "c")

        count = await cache_invalidate("blog:posts:*")
        assert count == 2
        assert await cache_get("blog:posts:all:1") is None
        assert await cache_get("blog:categories") == "c"

    async def test_invalidate_all(self):
        await cache_set("blog:posts:all:1", "a")
        await cache_set("blog:categories", "b")
        await cache_set("blog:tags", "c")

        count = await cache_invalidate_all()
        assert count == 3
        assert await cache_get("blog:posts:all:1") is None
        assert await cache_get("blog:categories") is None

    async def test_invalidate_empty(self):
        count = await cache_invalidate("blog:nothing:*")
        assert count == 0
