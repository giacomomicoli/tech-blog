"""Tests for the blog API endpoints."""

from unittest.mock import AsyncMock, PropertyMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(autouse=True)
def _no_cache():
    """Bypass Redis cache for all API tests to avoid event loop conflicts."""
    with (
        patch("src.api.posts.cache_get", new_callable=AsyncMock, return_value=None),
        patch("src.api.posts.cache_set", new_callable=AsyncMock),
    ):
        yield


@pytest.fixture
def client():
    return TestClient(app)


def _make_page(
    page_id: str = "page-1",
    title: str = "Test Post",
    slug: str = "test-post",
    published: bool = True,
    category: str | None = "Tech",
    tags: list[str] | None = None,
    published_date: str | None = "2026-02-01",
    excerpt: str = "An excerpt",
    author: str = "Alice",
    language: str = "it",
    hero_position: int | None = None,
    top: bool = False,
    related_post_ids: list[str] | None = None,
    meta_description: str | None = None,
    social_image: str | None = None,
    translation_key: str | None = None,
    translation_key_property_name: str = "Translation Key",
    last_edited_time: str = "2026-02-05T10:00:00.000Z",
) -> dict:
    """Build a mock Notion page object."""
    return {
        "id": page_id,
        "last_edited_time": last_edited_time,
        "properties": {
            "Name": {"type": "title", "title": [{"plain_text": title}]},
            "Slug": {"type": "rich_text", "rich_text": [{"plain_text": slug}]},
            "Excerpt": {"type": "rich_text", "rich_text": [{"plain_text": excerpt}]},
            "Meta Description": {
                "type": "rich_text",
                "rich_text": [{"plain_text": meta_description}] if meta_description else [],
            },
            "Category": {"type": "select", "select": {"name": category} if category else None},
            "Tags": {
                "type": "multi_select",
                "multi_select": [{"name": t} for t in (tags if tags is not None else ["python"])],
            },
            "Published Date": {
                "type": "date",
                "date": {"start": published_date} if published_date else None,
            },
            "Published": {"type": "checkbox", "checkbox": published},
            "Cover": {"type": "url", "url": None},
            "Social Image": {"type": "url", "url": social_image},
            "Author": {"type": "rich_text", "rich_text": [{"plain_text": author}]},
            "Language": {"type": "select", "select": {"name": language}},
            "Hero Position": {"type": "number", "number": hero_position},
            "Top": {"type": "checkbox", "checkbox": top},
            "Related Posts": {
                "type": "relation",
                "relation": [{"id": rid} for rid in (related_post_ids or [])],
            },
            translation_key_property_name: {
                "type": "rich_text",
                "rich_text": [{"plain_text": translation_key}] if translation_key else [],
            },
        },
    }


async def _mock_query_db(*args, **kwargs):
    """Async generator yielding mock pages."""
    pages = [
        _make_page("p1", "First Post", "first-post", category="Tech", tags=["python", "api"]),
        _make_page("p2", "Second Post", "second-post", category="Gaming", tags=["reviews"]),
    ]
    for p in pages:
        yield p


async def _mock_query_db_empty(*args, **kwargs):
    return
    yield  # make it an async generator


def _mock_blocks():
    return [
        {
            "type": "paragraph",
            "id": "b1",
            "paragraph": {
                "rich_text": [{"plain_text": "Hello world this is a test paragraph with words."}],
                "color": "default",
            },
        },
        {
            "type": "heading_2",
            "id": "h1",
            "heading_2": {
                "rich_text": [{"plain_text": "Section Title"}],
                "color": "default",
            },
        },
    ]


# ── /api/posts ─────────────────────────────────────────────


class TestListPosts:
    @patch("src.api.posts.notion_client")
    def test_list_posts(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["posts"]) == 2
        assert data["posts"][0]["slug"] == "first-post"
        assert data["page"] == 1

    @patch("src.api.posts.notion_client")
    def test_list_posts_empty(self, mock_client, client):
        mock_client.query_database = _mock_query_db_empty
        resp = client.get("/api/posts?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["posts"] == []

    @patch("src.api.posts.notion_client")
    def test_list_posts_pagination(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?limit=1&page=1&lang=it")
        data = resp.json()
        assert len(data["posts"]) == 1
        assert data["has_more"] is True

        resp2 = client.get("/api/posts?limit=1&page=2&lang=it")
        data2 = resp2.json()
        assert len(data2["posts"]) == 1
        assert data2["has_more"] is False

    @patch("src.api.posts.notion_client")
    def test_list_posts_filter_by_tag(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?tag=python&lang=it")
        assert resp.status_code == 200

    @patch("src.api.posts.notion_client")
    def test_list_posts_filter_by_category(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?category=Tech&lang=it")
        assert resp.status_code == 200

    @patch("src.api.posts.notion_client")
    def test_list_posts_default_lang(self, mock_client, client):
        """Omitting lang falls back to default locale."""
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts")
        assert resp.status_code == 200


# ── /api/posts/{slug} ─────────────────────────────────────


class TestGetPost:
    @patch("src.api.posts.notion_client")
    def test_get_post(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            filter_props = {
                condition.get("property") for condition in kwargs.get("filter", {}).get("and", [])
            }
            if "Slug" in filter_props:
                yield _make_page(
                    "p1",
                    "First Post",
                    "first-post",
                    meta_description="SEO description",
                    social_image="https://example.com/social.jpg",
                    translation_key="first-post",
                )
                return

            yield _make_page(
                "p1-it", "First Post IT", "primo-post", language="it", translation_key="first-post"
            )
            yield _make_page(
                "p1-en", "First Post EN", "first-post", language="en", translation_key="first-post"
            )

        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

        resp = client.get("/api/posts/first-post?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "first-post"
        assert data["title"] == "First Post"
        assert data["language"] == "it"
        assert "content_html" in data
        assert "table_of_contents" in data
        assert data["reading_time"] >= 1
        assert data["meta_description"] == "SEO description"
        assert data["social_image"] == "https://example.com/social.jpg"
        assert data["translation_key"] == "first-post"
        assert data["last_edited_time"] == "2026-02-05T10:00:00.000Z"
        assert data["alternates"] == {"it": "primo-post", "en": "first-post"}

    @patch("src.api.posts.notion_client")
    def test_get_post_not_found(self, mock_client, client):
        mock_client.query_database = _mock_query_db_empty
        resp = client.get("/api/posts/nonexistent?lang=it")
        assert resp.status_code == 404


# ── /api/categories ────────────────────────────────────────


class TestCategories:
    @patch("src.api.posts.notion_client")
    def test_list_categories(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/categories?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert "Tech" in data
        assert "Gaming" in data
        assert data == sorted(data)


# ── /api/tags ──────────────────────────────────────────────


class TestTags:
    @patch("src.api.posts.notion_client")
    def test_list_tags(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/tags?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert "python" in data
        assert "api" in data
        assert "reviews" in data
        assert data == sorted(data)


# ── /health ────────────────────────────────────────────────


class TestHealth:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ── Property extraction ────────────────────────────────────


class TestPropertyExtraction:
    """Test the helper functions via the API response structure."""

    @patch("src.api.posts.notion_client")
    def test_null_category(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(category=None)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["category"] is None

    @patch("src.api.posts.notion_client")
    def test_empty_tags(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(tags=[])

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["tags"] == []

    @patch("src.api.posts.notion_client")
    def test_featured_filter(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?featured=true&lang=it")
        assert resp.status_code == 200

    @patch("src.api.posts.notion_client")
    def test_null_date(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(published_date=None)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["published_date"] is None

    @patch("src.api.posts.notion_client")
    def test_language_in_response(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(language="en")

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=en")
        data = resp.json()
        assert data["posts"][0]["language"] == "en"

    @patch("src.api.posts.notion_client")
    def test_hero_position_extraction(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(hero_position=2)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["hero_position"] == 2

    @patch("src.api.posts.notion_client")
    def test_top_extraction(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(top=True)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["top"] is True

    @patch("src.api.posts.notion_client")
    def test_meta_description_falls_back_to_excerpt(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(meta_description=None, excerpt="Excerpt fallback")

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["meta_description"] == "Excerpt fallback"

    @patch("src.api.posts.notion_client")
    def test_translation_key_case_insensitive_lookup(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            filter_props = {
                condition.get("property") for condition in kwargs.get("filter", {}).get("and", [])
            }
            if "Slug" in filter_props:
                yield _make_page(
                    slug="case-post",
                    translation_key="shared-key",
                    translation_key_property_name="translation key",
                )
                return

            yield _make_page(slug="case-post", language="it", translation_key="shared-key")
            yield _make_page(slug="case-post-en", language="en", translation_key="shared-key")

        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

        resp = client.get("/api/posts/case-post?lang=it")
        data = resp.json()
        assert data["translation_key"] == "shared-key"
        assert data["alternates"] == {"it": "case-post", "en": "case-post-en"}

    @patch("src.api.posts.notion_client")
    def test_hero_position_null(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(hero_position=None)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["hero_position"] is None


# ── /api/posts/hero ───────────────────────────────────────


class TestHeroPosts:
    @patch("src.api.posts.notion_client")
    def test_hero_posts_sorted(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page("h1", "Hero 1", "hero-1", hero_position=1)
            yield _make_page("h2", "Hero 2", "hero-2", hero_position=2)
            yield _make_page("h3", "Hero 3", "hero-3", hero_position=3)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts/hero?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert data[0]["hero_position"] == 1
        assert data[1]["hero_position"] == 2
        assert data[2]["hero_position"] == 3

    @patch("src.api.posts.notion_client")
    def test_hero_posts_max_five(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            for i in range(1, 8):
                yield _make_page(f"h{i}", f"Hero {i}", f"hero-{i}", hero_position=i)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts/hero?lang=it")
        data = resp.json()
        assert len(data) == 5

    @patch("src.api.posts.notion_client")
    def test_hero_posts_empty(self, mock_client, client):
        mock_client.query_database = _mock_query_db_empty
        resp = client.get("/api/posts/hero?lang=it")
        assert resp.status_code == 200
        assert resp.json() == []

    @patch("src.api.posts.notion_client")
    def test_hero_posts_no_related_post_ids(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page("h1", "Hero 1", "hero-1", hero_position=1, related_post_ids=["r1"])

        mock_client.query_database = mock_query
        resp = client.get("/api/posts/hero?lang=it")
        data = resp.json()
        assert "related_post_ids" not in data[0]


# ── /api/posts/top ────────────────────────────────────────


class TestTopPosts:
    @patch("src.api.posts.notion_client")
    def test_top_posts(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page("t1", "Top 1", "top-1", top=True)
            yield _make_page("t2", "Top 2", "top-2", top=True)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts/top?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["top"] is True

    @patch("src.api.posts.notion_client")
    def test_top_posts_max_three(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            for i in range(1, 6):
                yield _make_page(f"t{i}", f"Top {i}", f"top-{i}", top=True)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts/top?lang=it")
        data = resp.json()
        assert len(data) == 3

    @patch("src.api.posts.notion_client")
    def test_top_posts_empty(self, mock_client, client):
        mock_client.query_database = _mock_query_db_empty
        resp = client.get("/api/posts/top?lang=it")
        assert resp.status_code == 200
        assert resp.json() == []

    @patch("src.api.posts.notion_client")
    def test_top_posts_no_related_post_ids(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page("t1", "Top 1", "top-1", top=True, related_post_ids=["r1"])

        mock_client.query_database = mock_query
        resp = client.get("/api/posts/top?lang=it")
        data = resp.json()
        assert "related_post_ids" not in data[0]


# ── Related posts in /api/posts/{slug} ────────────────────


class TestRelatedPosts:
    @patch("src.api.posts.notion_client")
    def test_related_posts_resolved(self, mock_client, client):
        related_page = _make_page("rel-1", "Related Post", "related-post", published=True)

        async def mock_query(*args, **kwargs):
            yield _make_page("p1", "Main Post", "main-post", related_post_ids=["rel-1"])

        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())
        mock_client.get_page = AsyncMock(return_value=related_page)

        resp = client.get("/api/posts/main-post?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["related_posts"]) == 1
        assert data["related_posts"][0]["slug"] == "related-post"
        assert "related_post_ids" not in data

    @patch("src.api.posts.notion_client")
    def test_related_posts_empty(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page("p1", "Main Post", "main-post", related_post_ids=[])

        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

        resp = client.get("/api/posts/main-post?lang=it")
        data = resp.json()
        assert data["related_posts"] == []
        assert "related_post_ids" not in data

    @patch("src.api.posts.notion_client")
    def test_related_posts_skip_unpublished(self, mock_client, client):
        unpublished_page = _make_page("rel-1", "Draft Post", "draft", published=False)

        async def mock_query(*args, **kwargs):
            yield _make_page("p1", "Main Post", "main-post", related_post_ids=["rel-1"])

        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())
        mock_client.get_page = AsyncMock(return_value=unpublished_page)

        resp = client.get("/api/posts/main-post?lang=it")
        data = resp.json()
        assert data["related_posts"] == []


# ── /api/pages/{page_slug} ────────────────────────────────


def _make_static_page(
    page_id: str = "page-1",
    title: str = "About",
    slug: str = "about-blog",
    language: str = "it",
    meta_description: str | None = None,
    social_image: str | None = None,
    translation_key: str | None = None,
    translation_key_property_name: str = "Translation Key",
    last_edited_time: str = "2026-02-05T10:00:00.000Z",
) -> dict:
    """Build a mock Notion page object for the Pages database."""
    return {
        "id": page_id,
        "last_edited_time": last_edited_time,
        "properties": {
            "Name": {"type": "title", "title": [{"plain_text": title}]},
            "Slug": {"type": "rich_text", "rich_text": [{"plain_text": slug}]},
            "Language": {"type": "select", "select": {"name": language}},
            "Meta Description": {
                "type": "rich_text",
                "rich_text": [{"plain_text": meta_description}] if meta_description else [],
            },
            "Social Image": {"type": "url", "url": social_image},
            translation_key_property_name: {
                "type": "rich_text",
                "rich_text": [{"plain_text": translation_key}] if translation_key else [],
            },
        },
    }


class TestStaticPages:
    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_about_blog_page(self, mock_client, mock_settings, client):
        async def mock_query(*args, **kwargs):
            filter_props = {
                condition.get("property") for condition in kwargs.get("filter", {}).get("and", [])
            }
            if "Slug" in filter_props:
                yield _make_static_page(
                    "page-abc",
                    "About This Blog",
                    "about-blog",
                    meta_description="About description",
                    social_image="https://example.com/about.jpg",
                    translation_key="about-blog",
                )
                return

            yield _make_static_page(
                "page-it",
                "About This Blog",
                "about-blog",
                language="it",
                translation_key="about-blog",
            )
            yield _make_static_page(
                "page-en",
                "About This Blog",
                "about-blog",
                language="en",
                translation_key="about-blog",
            )

        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

        resp = client.get("/api/pages/about-blog?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "page-abc"
        assert data["slug"] == "about-blog"
        assert data["title"] == "About This Blog"
        assert "content_html" in data
        assert data["meta_description"] == "About description"
        assert data["social_image"] == "https://example.com/about.jpg"
        assert data["translation_key"] == "about-blog"
        assert data["last_edited_time"] == "2026-02-05T10:00:00.000Z"
        assert data["alternates"] == {"it": "about-blog", "en": "about-blog"}

    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_about_me_page(self, mock_client, mock_settings, client):
        async def mock_query(*args, **kwargs):
            yield _make_static_page("page-def", "About Me", "about-me")

        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

        resp = client.get("/api/pages/about-me?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "about-me"
        assert data["title"] == "About Me"

    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_page_translation_key_case_insensitive_lookup(
        self, mock_client, mock_settings, client
    ):
        async def mock_query(*args, **kwargs):
            filter_props = {
                condition.get("property") for condition in kwargs.get("filter", {}).get("and", [])
            }
            if "Slug" in filter_props:
                yield _make_static_page(
                    "page-abc",
                    "About This Blog",
                    "about-blog",
                    translation_key="about-blog",
                    translation_key_property_name="translation key",
                )
                return

            yield _make_static_page(
                "page-it", "About", "about-blog", language="it", translation_key="about-blog"
            )
            yield _make_static_page(
                "page-en", "About", "about-blog", language="en", translation_key="about-blog"
            )

        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

        resp = client.get("/api/pages/about-blog?lang=it")
        data = resp.json()
        assert data["translation_key"] == "about-blog"
        assert data["alternates"] == {"it": "about-blog", "en": "about-blog"}

    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_page_database_not_accessible(self, mock_client, mock_settings, client):
        from src.notion.client import NotionNotFound

        async def mock_query(*args, **kwargs):
            raise NotionNotFound(404, "object_not_found", "Database not found")
            yield

        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = mock_query

        resp = client.get("/api/pages/about-blog?lang=it")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Pages database not accessible"

    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_page_slug_not_found(self, mock_client, mock_settings, client):
        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = _mock_query_db_empty

        resp = client.get("/api/pages/nonexistent?lang=it")
        assert resp.status_code == 404

    @patch("src.api.posts.settings")
    def test_get_page_database_not_configured(self, mock_settings, client):
        mock_settings.notion_pages_data_source_id = ""
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        resp = client.get("/api/pages/about-blog?lang=it")
        assert resp.status_code == 404

    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_page_blocks_not_found(self, mock_client, mock_settings, client):
        from src.notion.client import NotionNotFound

        async def mock_query(*args, **kwargs):
            yield _make_static_page("page-abc", "About", "about-blog")

        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(
            side_effect=NotionNotFound(404, "not_found", "Not found")
        )

        resp = client.get("/api/pages/about-blog?lang=it")
        assert resp.status_code == 404
