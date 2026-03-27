# Testing & Linting

> Authoritative reference for AI agents and developers. This document describes the current
> testing infrastructure, test patterns, and linting configuration. Follow these patterns
> when adding or modifying tests.

## Overview

| Layer | Framework | Runner | Count |
|-------|-----------|--------|-------|
| Backend | pytest + pytest-asyncio + fakeredis | `make test-backend` | 74 tests |
| Frontend | vitest + @vue/test-utils + happy-dom | `make test-frontend` | 22 tests |
| Linting | ruff (check + format) | `make lint` | — |

All tests run inside Docker containers to ensure consistent environments.

## Running Tests

```bash
make test             # Run all tests (backend + frontend)
make test-backend     # pytest tests/ -v (inside Docker)
make test-frontend    # vitest run (inside Docker)
make lint             # ruff check + ruff format --check on backend/src/
```

### Running a Single Backend Test

```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
    exec backend pytest tests/test_renderer.py::TestRenderBlocks::test_paragraph -v
```

### Running Frontend Tests in Watch Mode

```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
    exec frontend npx vitest --watch
```

## Backend Tests

### Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

All async test functions are automatically detected — no need for `@pytest.mark.asyncio`.

### Fixtures (`conftest.py`)

#### `fake_redis` (autouse=True, session-scoped logic)

- Patches `src.cache._redis` to `None` before each test
- Monkeypatches `get_redis()` to return a fresh `fakeredis.aioredis.FakeRedis` instance per call
- Cleans up all instances after each test
- Prevents event-loop contamination between tests

#### `_no_cache` (autouse=True, in `test_api.py`)

- Patches `cache_get` to return `None` (cache miss)
- Patches `cache_set` to no-op
- Ensures API tests always hit the mocked Notion client, never Redis

#### `client`

- Returns `TestClient(app)` — FastAPI's sync test client
- Used in all API test methods

### Test Files

#### `test_api.py` — API Endpoint Tests

**Helper functions**:

```python
def _make_page(page_id, title, slug, published, category, tags, published_date, excerpt, author, language="it")
# Builds a mock Notion page object with all expected properties including Language

def _make_static_page(page_id, title, slug)
# Builds a mock Notion page for the Pages database (Name + Slug only)

async def _mock_query_db(*args, **kwargs)
# Async generator yielding 2 sample posts (First Post/Tech, Second Post/Gaming)

async def _mock_query_db_empty(*args, **kwargs)
# Empty async generator (no results)

def _mock_blocks()
# Returns list with 1 paragraph + 1 heading_2 block
```

**Test classes**:

| Class | Tests | What It Covers |
|-------|-------|---------------|
| `TestListPosts` | 7 | List, empty, pagination, tag filter, category filter, default lang, language in response |
| `TestGetPost` | 2 | Full post fetch, 404 on missing slug |
| `TestCategories` | 1 | Sorted unique categories |
| `TestTags` | 1 | Sorted unique tags |
| `TestHealth` | 1 | Health check endpoint |
| `TestPropertyExtraction` | 4 | Null category, empty tags, featured filter, null date |
| `TestStaticPages` | 5 | About blog, about me, slug not found, DB not configured, blocks not found |

**Mocking pattern**: All API tests use `@patch("src.api.posts.notion_client")` to mock the
Notion client. For database queries, replace `mock_client.query_database` with an async
generator function. For block fetches, set `mock_client.get_blocks = AsyncMock(return_value=...)`.

For static page tests, also patch `@patch("src.api.posts.settings")` to set
`notion_pages_data_source_id`, `parsed_locales`, and `default_locale`.

**Example mock pattern**:
```python
@patch("src.api.posts.notion_client")
def test_get_post(self, mock_client, client):
    async def mock_query(*args, **kwargs):
        yield _make_page("p1", "First Post", "first-post")

    mock_client.query_database = mock_query
    mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

    resp = client.get("/api/posts/first-post?lang=it")
    assert resp.status_code == 200
```

#### `test_cache.py` — Cache Tests

**Test classes**:

| Class | Tests | What It Covers |
|-------|-------|---------------|
| `TestKeyHelpers` | 7 | All key pattern functions, suffix combinations |
| `TestCacheOperations` | 7 | Set/get, missing key, overwrite, complex data, invalidation patterns |

Uses `fakeredis` for real Redis operations without a running Redis server.

#### `test_config.py` — Settings Tests

| Class | Tests | What It Covers |
|-------|-------|---------------|
| `TestSettings` | 2 | Redis password secret injection into `redis_url`, unchanged URL when secret is missing |

**Key pattern examples tested**:
```python
posts_list_key("it")                              → "blog:it:posts:all:1"
posts_list_key("en", tag="python")                → "blog:en:posts:tag:python:1"
posts_list_key("it", category="Tech")             → "blog:it:posts:cat:Tech:1"
posts_list_key("it", category="Tech", page=2)     → "blog:it:posts:cat:Tech:2"
posts_list_key("it", featured=True)               → "blog:it:posts:all:featured:True:1"
post_key("it", "my-post")                         → "blog:it:posts:my-post"
page_key("it", "about-blog")                      → "blog:it:page:about-blog"
categories_key("it")                              → "blog:it:categories"
tags_key("it")                                    → "blog:it:tags"
```

#### `test_renderer.py` — Renderer Tests

**Helper functions**:
```python
def _rt(text, bold=False, italic=False, strikethrough=False, underline=False,
        code=False, color="default", href=None)
# Build a rich_text item with annotations

def _block(block_type, rich_text_items=None, block_id="blk1", color="default",
           children=None, **extra)
# Build a minimal Notion block
```

**Test classes**:

| Class | Tests | What It Covers |
|-------|-------|---------------|
| `TestRenderRichText` | 11 | All annotations, colors, links, escaping, equations, empty |
| `TestRenderBlocks` | 17 | All block types, list grouping, nesting, unsupported blocks |
| `TestExtractToc` | 3 | TOC from headings, recursive children, empty |

**Key rendering tests**:
- Annotations nest correctly: `<strong><em>text</em></strong>`
- HTML is escaped: `<script>` → `&lt;script&gt;`
- Consecutive bulleted list items grouped into single `<ul>`
- A paragraph between two bulleted lists creates two separate `<ul>` elements
- Heading IDs are block UUIDs with hyphens removed
- Code blocks include `class="language-{lang}"`
- Callouts include icon span + content div
- Tables respect `has_column_header` for `<th>` vs `<td>`
- Unsupported block types are silently skipped (no error, no output)

### Adding New Backend Tests

1. Place test file in `backend/tests/`
2. Name it `test_{module}.py`
3. Use `TestClient(app)` for API tests, fakeredis fixtures for cache tests
4. Mock Notion client with `@patch("src.api.posts.notion_client")`
5. Use `_make_page()` helper for mock page objects
6. Async generators for `query_database`, `AsyncMock` for `get_blocks`/`get_page`

## Frontend Tests

### Configuration

Vitest configured in `nuxt.config.ts` or `vitest.config.ts`. Uses `happy-dom` as the DOM
implementation (lighter than jsdom).

### Test Files

All in `frontend/tests/components/`:

#### `PostCard.test.ts`

Tests the PostCard component rendering:
- Renders post title and excerpt
- Links to correct locale-prefixed blog post URL (`/{lang}/blog/{slug}`)
- Shows cover image when available, hides when null
- Formats date correctly using locale-aware formatting
- Uses `$t()` for translatable strings

#### `PostMeta.test.ts`

Tests the PostMeta component:
- Shows author name
- Renders category link to `/{lang}/category/{name}`
- Renders tag links to `/{lang}/tag/{name}`
- Hides sections when data is null/empty

#### `TableOfContents.test.ts`

Tests the TableOfContents component:
- Renders all entries as anchor links
- Links point to `#{id}` anchors
- Applies `.toc-level-2` and `.toc-level-3` classes
- Renders nothing when entries array is empty

### Test Patterns

```typescript
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import PostCard from '~/components/PostCard.vue'

describe('PostCard', () => {
    const post = { /* mock post data */ }

    it('renders the title', () => {
        const wrapper = mount(PostCard, { props: { post } })
        expect(wrapper.text()).toContain(post.title)
    })
})
```

NuxtLink is stubbed in tests — use `wrapper.findComponent({ name: 'NuxtLink' })` or
check the rendered `<a>` tags.

### Adding New Frontend Tests

1. Place test file in `frontend/tests/components/`
2. Name it `{ComponentName}.test.ts`
3. Use `@vue/test-utils` `mount()` with props
4. Stub NuxtLink and other Nuxt components as needed
5. Test rendering output, class presence, link hrefs, and conditional visibility

## Linting

### Ruff Configuration (`pyproject.toml`)

```toml
[tool.ruff]
target-version = "py312"
line-length = 100
```

### Commands

```bash
make lint
# Runs:
#   cd backend && uvx ruff check src/     # Check for lint errors
#   cd backend && uvx ruff format --check src/  # Check formatting
```

`uvx` runs ruff without requiring it in the project's virtualenv.

### Key Rules

- Target Python 3.12 features (union types with `|`, etc.)
- 100 character line length
- Unused imports flagged as errors
- Standard ruff defaults (pyflakes, pycodestyle, isort)

### Fixing Lint Issues

```bash
cd backend && uvx ruff check src/ --fix      # Auto-fix lint errors
cd backend && uvx ruff format src/            # Auto-format code
```

## CI Expectations

When making changes:
1. All 72 backend tests must pass: `make test-backend`
2. All 22 frontend tests must pass: `make test-frontend`
3. `ruff check` must pass with no errors: `make lint`
4. New features should include tests following the patterns above
