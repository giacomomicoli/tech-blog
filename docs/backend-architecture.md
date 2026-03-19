# Backend Architecture

> Authoritative reference for AI agents and developers. This document describes the current
> implementation of the backend. Do not deviate from these patterns, response shapes, or
> conventions when making changes.

## Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app, lifespan, CORS, health check, cache invalidation
│   ├── config.py            # Pydantic Settings with Docker secrets support
│   ├── cache.py             # Redis async client, key patterns, TTL
│   ├── api/
│   │   ├── __init__.py
│   │   └── posts.py         # REST endpoints: posts, categories, tags, pages
│   └── notion/
│       ├── __init__.py
│       ├── client.py        # Notion API client with rate limiting and pagination
│       ├── renderer.py      # Notion blocks → HTML conversion (20+ block types)
│       └── sync.py          # Background polling loop for cache invalidation
├── tests/
│   ├── conftest.py          # Fixtures: fakeredis, event loop isolation
│   ├── test_api.py          # API endpoint tests with TestClient
│   ├── test_cache.py        # Cache key patterns and operations
│   └── test_renderer.py     # Block rendering and TOC extraction
├── Dockerfile               # Multi-stage: python:3.12-slim, uv package manager
└── pyproject.toml           # Dependencies, ruff config, pytest config
```

## Dependencies

```
fastapi>=0.115      # Web framework
uvicorn[standard]   # ASGI server
httpx>=0.28         # Async HTTP client (for Notion API)
redis[hiredis]>=5.2 # Async Redis client
pydantic>=2.10      # Data validation
pydantic-settings   # Settings from env/secrets
```

Dev: `pytest`, `pytest-asyncio`, `fakeredis`, `ruff`

## Configuration (`config.py`)

All settings use Pydantic v2 `BaseSettings`. Values are read from `.env` file first, then
Docker secrets at `/run/secrets/{field_name}` override them in `model_post_init`.

```python
class Settings(BaseSettings):
    notion_api_key: str = ""
    notion_database_id: str = ""
    notion_data_source_id: str = ""
    notion_api_version: str = "2025-09-03"
    redis_url: str = "redis://redis:6379/0"
    cache_ttl_seconds: int = 300
    cache_invalidate_secret: str = ""
    notion_pages_data_source_id: str = ""
    sync_interval_minutes: int = 5
    backend_port: int = 8000
    supported_locales: str = "it,en"
    default_locale: str = "it"

    @property
    def parsed_locales(self) -> list[str]:
        return [loc.strip() for loc in self.supported_locales.split(",") if loc.strip()]
```

Fields checked for Docker secrets: `notion_api_key`, `notion_database_id`,
`notion_data_source_id`, `cache_invalidate_secret`, `notion_pages_data_source_id`.

Singleton: `settings = Settings()` at module level.

## App Entrypoint (`main.py`)

### Lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    sync_task = asyncio.create_task(sync_loop())
    yield
    sync_task.cancel()
    await notion_client.close()
    await close_redis()
```

### Middleware & Routes

- **CORS**: All origins, all methods, all headers (wide open for flexibility)
- **Router**: `api/posts.py` mounted with prefix `/api`
- **Health check**: `GET /health` → `{"status": "ok"}`
- **Cache invalidation**: `POST /api/cache/invalidate` with `Authorization: Bearer {secret}` → `{"invalidated": count}`

## Notion Client (`notion/client.py`)

### Singleton

```python
notion_client = NotionClient()  # Module-level, uses settings defaults
```

### Exception Hierarchy

```
NotionAPIError(status, code, message)
├── NotionRateLimited   # 429
├── NotionNotFound      # 404
└── NotionUnauthorized  # 401
```

### Rate Limiter

Token-bucket style, 3 requests/second. Uses `asyncio.Lock` and `time.monotonic()`.
Every call to `_request()` calls `_rate_limiter.acquire()` first.

### Retry Logic

On HTTP 429: retry up to `MAX_RETRIES=3` times with exponential backoff
(`retry_after * 2^attempt`). Uses the `Retry-After` header (default 1 second).

### HTTP Client

- Library: `httpx.AsyncClient`
- Base URL: `https://api.notion.com/v1`
- Headers: `Authorization: Bearer {key}`, `Notion-Version: {version}`, `Content-Type: application/json`
- Timeout: 30 seconds
- Lazy-initialized, singleton per `NotionClient` instance

### Pagination

`_paginate()` handles both POST and GET paginated endpoints. Uses `page_size=100`,
follows `next_cursor` until `has_more` is false. Yields individual items.

### Public Methods

| Method | Notion Endpoint | Returns |
|--------|----------------|---------|
| `query_database(data_source_id?, filter?, sorts?)` | `POST /data_sources/{id}/query` | `AsyncGenerator[dict]` of page objects |
| `get_page(page_id)` | `GET /pages/{id}` | Single page dict |
| `get_blocks(block_id)` | `GET /blocks/{id}/children` | `list[dict]` with recursive children |
| `search(query?, filter?)` | `POST /search` | `AsyncGenerator[dict]` |

`get_blocks()` recursively fetches children: if a block has `has_children=true`,
it calls `get_blocks(block["id"])` and stores the result in `block["children"]`.

`query_database()` defaults to `settings.notion_data_source_id` but accepts an override
(used by the Pages endpoint to query `settings.notion_pages_data_source_id`).

## API Endpoints (`api/posts.py`)

### Property Extraction Helpers

These functions extract typed values from Notion page property objects:

| Function | Input | Output |
|----------|-------|--------|
| `_get_plain_text(prop)` | title or rich_text property | `str` |
| `_get_select(prop)` | select property | `str \| None` |
| `_get_multi_select(prop)` | multi_select property | `list[str]` |
| `_get_date(prop)` | date property | `str \| None` (ISO format) |
| `_get_checkbox(prop)` | checkbox property | `bool` |
| `_get_url(prop)` | url property | `str \| None` |
| `_get_number(prop)` | number property | `int \| None` |
| `_get_relation_ids(prop)` | relation property | `list[str]` (page IDs) |

`_extract_post_meta(page)` combines all helpers to produce a post metadata dict:
```python
{
    "id": str, "slug": str, "title": str, "excerpt": str,
    "category": str | None, "tags": list[str],
    "published_date": str | None, "cover_image": str | None,
    "author": str, "featured": bool, "language": str,
    "hero_position": int | None, "top": bool,
    "related_post_ids": list[str]  # internal only, stripped from API responses
}
```

`_estimate_reading_time(blocks)` counts words recursively across all blocks at ~200 words/min. Minimum 1 minute.

### GET /api/posts

Query params: `lang?`, `tag?`, `category?`, `featured?`, `page=1` (ge=1), `limit=10` (ge=1, le=50)

The `lang` parameter selects the content language (validated against `supported_locales`, defaults to `default_locale`). Filter always includes `Published = true` and `Language = {lang}`. Additional filters are ANDed. Sorts by
`Published Date` descending. Client-side pagination (all results fetched, then sliced).

Response:
```json
{
    "posts": [{ "id", "slug", "title", "excerpt", "category", "tags",
                "published_date", "cover_image", "author", "featured", "language" }],
    "total": int,
    "page": int,
    "has_more": bool
}
```

### GET /api/posts/hero

**Important**: Registered before `/posts/{slug}` to avoid FastAPI matching "hero" as a slug.

Query params: `lang?`

Filter: `Published=true AND Language={lang} AND Hero Position is_not_empty`. Sorted by `Hero Position` ascending. Returns up to 5 posts.

Response: `[{ post metadata without related_post_ids }]`

### GET /api/posts/top

**Important**: Registered before `/posts/{slug}` to avoid FastAPI matching "top" as a slug.

Query params: `lang?`

Filter: `Published=true AND Language={lang} AND Top=true`. Sorted by `Published Date` descending. Returns up to 3 posts.

Response: `[{ post metadata without related_post_ids }]`

### GET /api/posts/{slug}

Queries database with `Published=true AND Slug={slug} AND Language={lang}`. Fetches blocks, renders HTML,
extracts TOC, estimates reading time. Resolves `related_post_ids` by fetching each related page via
`notion_client.get_page()`, extracting meta, and filtering to only published posts. Accepts `lang` query parameter.

Response: post metadata + `content_html`, `table_of_contents`, `reading_time`, `related_posts: Post[]`.
The `related_post_ids` field is removed from the response.

404 if slug not found or blocks not accessible.

### GET /api/categories

Queries all published posts for the given `lang`, extracts unique Category values, returns sorted list.

Response: `["Gaming", "Tech", ...]`

### GET /api/tags

Same pattern as categories but for Tags multi-select. Accepts `lang` query parameter.

Response: `["api", "python", ...]`

### GET /api/pages/{slug}

Queries the **Pages** database (`settings.notion_pages_data_source_id`) by `Slug` property
and `Language` filter. Accepts `lang` query parameter.
Returns 404 if the pages database is not configured, if the slug is not found, or if
blocks are not accessible.

Response:
```json
{ "slug": "about-blog", "title": "About This Blog", "content_html": "<p>...</p>" }
```

## Cache Layer (`cache.py`)

### Connection

Singleton `aioredis.Redis` with `decode_responses=True`. Lazy-initialized on first use.

### Key Patterns

All keys prefixed with `blog:` and include the language code:

| Function | Pattern | Example |
|----------|---------|---------|
| `posts_list_key(lang, tag?, category?, featured?, page)` | `blog:{lang}:posts:{suffix}:{page}` | `blog:it:posts:all:1`, `blog:en:posts:tag:python:1` |
| `post_key(lang, slug)` | `blog:{lang}:posts:{slug}` | `blog:it:posts:hello-world` |
| `page_key(lang, slug)` | `blog:{lang}:page:{slug}` | `blog:it:page:about-blog` |
| `categories_key(lang)` | `blog:{lang}:categories` | `blog:it:categories` |
| `tags_key(lang)` | `blog:{lang}:tags` | `blog:it:tags` |
| `hero_key(lang)` | `blog:{lang}:hero` | `blog:it:hero` |
| `top_key(lang)` | `blog:{lang}:top` | `blog:it:top` |

### Operations

| Function | Behavior |
|----------|----------|
| `cache_get(key)` | Returns deserialized JSON or `None` |
| `cache_set(key, value, ttl?)` | JSON-serializes with `default=str`, sets with TTL (default 300s) |
| `cache_invalidate(pattern)` | Deletes keys matching glob pattern via `SCAN`, returns count |
| `cache_invalidate_all()` | Calls `cache_invalidate("blog:*")` |

## Renderer (`notion/renderer.py`)

### Rich Text Processing

`render_rich_text(items)` converts Notion rich_text array to HTML:

1. HTML-escapes all plain text (`html.escape()`)
2. Wraps with annotation tags in order: `<strong>`, `<em>`, `<del>`, `<u>`, `<code>`
3. Applies color as inline `style` attribute (foreground or background)
4. Wraps in `<a href="..." target="_blank" rel="noopener">` if link present
5. Handles `equation` type items as `<span class="inline-equation" data-equation="...">`

### Color Map

18 Notion colors mapped to hex values. Foreground colors (e.g. `gray` → `#787774`)
use `color` CSS property. Background colors (e.g. `gray_background` → `#F1F1EF`)
use `background-color`.

### Supported Block Types

| Block Type | HTML Output |
|------------|-------------|
| `paragraph` | `<p>` with optional color style |
| `heading_1/2/3` | `<h1/2/3 id="{block_id_no_hyphens}">` |
| `bulleted_list_item` | `<li>` grouped in `<ul>` |
| `numbered_list_item` | `<li>` grouped in `<ol>` |
| `to_do` | `<li class="todo-item">` with checkbox, grouped in `<ul class="todo-list">` |
| `toggle` | `<details><summary>` |
| `quote` | `<blockquote>` |
| `callout` | `<div class="callout">` with `<span class="callout-icon">` + `<div class="callout-content">` |
| `code` | `<pre><code class="language-{lang}">` with optional `<figcaption>` |
| `equation` | `<div class="equation" data-equation="...">` |
| `divider` | `<hr>` |
| `image` | `<figure><img loading="lazy">` with optional caption |
| `video` | `<iframe>` for YouTube/Vimeo, `<video>` for direct URLs |
| `bookmark` | `<a class="bookmark">` |
| `embed` | `<figure><iframe>` |
| `table` | `<table>` with `<thead>`/`<tbody>`, respects `has_column_header` |
| `column_list` | `<div class="columns">` with `<div class="column">` children |
| `child_page` | `<a class="child-page" href="/blog/{id}">` |
| `link_to_page` | `<a class="link-to-page" href="/blog/{id}">` |
| `synced_block` | Renders children directly |
| `table_of_contents` | Empty string (frontend handles TOC) |
| `breadcrumb` | Empty string |

Unsupported block types are silently skipped.

### List Grouping

`render_blocks()` groups consecutive list items of the same type into a single `<ul>`
or `<ol>` wrapper. A non-list block between two list blocks creates two separate lists.

### TOC Extraction

`extract_toc(blocks)` returns a flat list of heading entries:
```python
[{"id": "blockidnohyphens", "text": "Heading text", "level": 2}]
```
Recursively processes children. Heading IDs are block UUIDs with hyphens removed.

## Background Sync (`notion/sync.py`)

### Loop

Runs as an `asyncio.Task` created during app lifespan. Sleeps for `sync_interval_minutes * 60`
seconds between checks. All exceptions caught and logged — the loop never crashes.

### Update Detection

`_check_for_updates(known_edits)` maintains a dict of `{page_id: last_edited_time}`.
Each iteration:

1. Queries database sorted by `last_edited_time` descending (up to 20 pages)
2. For each page, compares `last_edited_time` with stored value
3. If changed:
   - Invalidates `blog:*:posts:{slug}` for that specific post (all languages)
   - Invalidates `blog:*:posts:*` (all listing caches across all languages)
   - Invalidates `blog:*:hero` (hero caches across all languages)
   - Invalidates `blog:*:top` (top caches across all languages)
4. Updates `known_edits` with new timestamps

Note: Categories and tags caches are NOT invalidated by the sync loop — only by the
manual `POST /api/cache/invalidate` endpoint.

## Error Handling Patterns

- Notion 404 → `HTTPException(404)` with descriptive detail
- Missing configuration → `HTTPException(404, "not configured")`
- Notion rate limits → automatic retry with backoff (never surfaces to client)
- Sync loop errors → logged and swallowed, loop continues
- All text rendered by the renderer is HTML-escaped to prevent XSS

See `docs/testing-and-linting.md` for linting configuration and ruff settings.
