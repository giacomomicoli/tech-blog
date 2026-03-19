# AGENTS.md

Guidance for AI coding agents working in this repository.
For deeper details, consult the `docs/` directory (especially `docs/backend-architecture.md`,
`docs/frontend-architecture.md`, `docs/docker-and-deployment.md`, `docs/coding-standards.md`,
and `docs/notion-setup.md`).

## Project Overview

"TECH.md" — a Notion-powered blog CMS: Python FastAPI backend, Nuxt 3 (Vue 3 / TypeScript)
frontend, Redis caching, Docker Swarm deployment with Traefik reverse proxy (shared across
services). Local development uses Caddy as a lightweight reverse proxy. All services run in
Docker.

## Environment Setup

Copy `.env.example` to `.env` and fill in Notion credentials.
Key required variables: `NOTION_API_KEY`, `NOTION_DATABASE_ID`, `NOTION_DATA_SOURCE_ID`,
`CACHE_INVALIDATE_SECRET`.

## Repository Structure

```
├── .github/workflows/ # CI (lint + test) and Deploy (build, push, deploy) pipelines
├── backend/           # Python FastAPI backend (src/, tests/, Dockerfile)
├── frontend/          # Nuxt 3 frontend (components, pages, composables, Dockerfile)
├── docker/            # Compose files (base, dev, prod), Caddyfile, deploy script
├── docs/              # Architecture and reference documentation
├── Makefile           # All build/test/lint/deploy commands
├── .env.example       # Environment template
├── CHANGELOG.md       # Version history (Keep a Changelog format)
└── AGENTS.md          # This file
```

### Documentation Index

| Document | What It Covers |
|----------|---------------|
| [`docs/project-overview.md`](docs/project-overview.md) | Branding, tech stack, architecture diagram, Notion database schemas, environment variables, API endpoints, frontend routes, design principles |
| [`docs/backend-architecture.md`](docs/backend-architecture.md) | File structure, config/secrets, Notion client (rate limiter, retry, pagination), API endpoint signatures and response shapes, cache key patterns, renderer (20+ block types), sync loop, error handling |
| [`docs/frontend-architecture.md`](docs/frontend-architecture.md) | Nuxt config, SSR setup, all components (props, state, CSS classes), all pages, useApi composable, TypeScript interfaces, theme system (design tokens, how to add themes), server routes (RSS/sitemap), Dockerfile |
| [`docs/coding-standards.md`](docs/coding-standards.md) | Python and TypeScript naming conventions, component structure template, CSS rules (theme tokens, BEM naming, responsive breakpoints, accessibility), API contract, i18n conventions, file organization rules |
| [`docs/docker-and-deployment.md`](docs/docker-and-deployment.md) | All 3 compose files (base/dev/prod), Caddyfile, Traefik labels, CI/CD pipelines, ghcr.io registry, deploy script, Dockerfiles, Docker secrets, resource limits, server architecture, dev vs prod differences |
| [`docs/testing-and-linting.md`](docs/testing-and-linting.md) | Test infrastructure (pytest/vitest), all test classes and counts, mock patterns and fixtures, how to add new tests, ruff config |
| [`docs/notion-setup.md`](docs/notion-setup.md) | Notion database property definitions for Posts and Pages databases, setup steps, how to create about pages |

## Git Workflow

### Branches

| Branch    | Purpose    | Deploys to  | Direct push |
|-----------|------------|-------------|-------------|
| `dev`     | Integration branch for all features and fixes | --          | Yes         |
| `release` | Staging / pre-production verification         | Staging     | No (PR from `dev`)     |
| `main`    | Production                                    | Production  | No (PR from `release`) |

### Flow

1. Work on `dev` -- all feature and fix commits go here
2. When ready to stage: open a PR from `dev` -> `release`, merge
3. When verified in staging: open a PR from `release` -> `main`, merge
4. After merging to `main`: tag the new version
5. Rebase `release` and `dev` onto `main` to keep all branches aligned:

```bash
git checkout release && git rebase main && git push
git checkout dev && git rebase main && git push
```

**Never push directly to `release` or `main`.**

### Versioning

Follow [Keep a Changelog](https://keepachangelog.com/) standards. Tag releases on `main`
after merging from `release`:

```bash
git tag -a v1.2.0 -m "v1.2.0"
git push origin v1.2.0
```

Version bumps follow semver:
- **Major** (v2.0.0): breaking changes to API contracts or deployment
- **Minor** (v1.1.0): new features, new endpoints, new components
- **Patch** (v1.0.1): bug fixes, style fixes, dependency updates

### Changelog Maintenance

After every change, update `CHANGELOG.md`:
1. Add entries under the `[Unreleased]` section
2. Use subsections: `Added`, `Changed`, `Fixed`, `Removed`
3. Group entries by area: `Backend`, `Frontend`, `Infrastructure`, `Documentation`
4. When releasing, move `[Unreleased]` items to a versioned heading with the date

If your changes affect conventions described in this file or in `docs/`, update the
relevant documentation in the same commit.

## CI/CD

Two GitHub Actions workflows automate testing and deployment:

- **CI** (`.github/workflows/ci.yml`): Runs lint (ruff), backend tests (pytest), and frontend
  tests (vitest) on every push/PR to `dev`, `release`, `main`. No Docker required.
- **Deploy** (`.github/workflows/deploy.yml`): On push to `main`, builds Docker images, pushes
  to ghcr.io, then SSHs into the VPS to deploy the Swarm stack with the new image tag.

Images are stored at `ghcr.io/giacomomicoli/tech-blog/{backend,frontend}` and tagged with
both `latest` and the git commit SHA. See `docs/docker-and-deployment.md` for full details.

## Build & Run

```bash
make dev              # Build and start all containers (detached, hot reload)
make dev-down         # Stop all containers
make dev-rebuild      # Full rebuild with volume reset
make logs             # Follow all service logs
make logs-backend     # Backend logs only
make logs-frontend    # Frontend logs only
make backend-shell    # Shell into backend container
make frontend-shell   # Shell into frontend container
make prod-deploy      # Create Docker secrets, deploy Swarm stack
make prod-down        # Remove Swarm stack
```

## Testing

All tests run inside Docker containers. Containers must be running (`make dev`) first.

```bash
make test             # Run all tests (backend + frontend)
make test-backend     # pytest tests/ -v
make test-frontend    # vitest run
```

### Single backend test

```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
    exec backend pytest tests/test_renderer.py::TestRenderBlocks::test_paragraph -v
```

Pattern: `tests/{test_file}.py::TestClassName::test_method_name`

### Single frontend test

```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
    exec frontend npx vitest run tests/components/PostCard.test.ts
```

### Frontend watch mode

```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
    exec frontend npx vitest --watch
```

## Linting

```bash
make lint                                    # ruff check + format check
cd backend && uvx ruff check src/ --fix      # Auto-fix lint errors
cd backend && uvx ruff format src/           # Auto-format code
```

Ruff config (in `pyproject.toml`): Python 3.12, line length 100, default rule set.
No ESLint configured for the frontend.

## Python Code Style (Backend)

### Imports

Three groups separated by blank lines: stdlib, third-party, local.

```python
import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from src.config import settings
from src.cache import cache_get, cache_set
```

### Naming

| Element            | Convention          | Example                              |
|--------------------|---------------------|--------------------------------------|
| Functions          | `snake_case`        | `get_post`, `cache_invalidate`       |
| Private helpers    | `_snake_case`       | `_get_plain_text`, `_render_heading` |
| Classes            | `PascalCase`        | `NotionClient`, `Settings`           |
| Constants          | `UPPER_SNAKE_CASE`  | `PREFIX`, `MAX_RETRIES`, `BASE_URL`  |
| Module singletons  | `snake_case`        | `notion_client`, `settings`          |
| API response keys  | `snake_case`        | `content_html`, `reading_time`       |

### Types & Formatting

- Python 3.12+ syntax: `str | None` (not `Optional[str]`), `list[dict]`, `dict[str, Any]`
- Return type annotations on all public functions
- Line length: 100 characters
- Double quotes for strings
- Section separators: `# ── Section Name ─────────────────────`

### Error Handling

- Notion 404 -> `HTTPException(status_code=404, detail="Post not found")`
- Missing config -> `HTTPException(404, "not configured")` (not 500)
- Background tasks: catch all exceptions, log with `logger.exception()`, continue loop
- Never expose internal details in error responses

### Async Patterns

- All I/O uses async/await -- no blocking calls
- Lazy singletons via `global _redis` pattern with `async def get_redis()`
- Async generators (`AsyncGenerator[dict, None]`) for paginated Notion queries
- Cache-first: every endpoint checks `cache_get()` before fetching from Notion

### API Response Shapes

All responses are plain dicts (not Pydantic models), `snake_case` keys:

- `GET /api/posts` -> `{ posts: [...], total, page, has_more }`
- `GET /api/posts/{slug}` -> post meta + `content_html`, `table_of_contents`, `reading_time`
- `GET /api/categories` / `GET /api/tags` -> sorted `string[]`
- `GET /api/pages/{slug}` -> `{ slug, title, content_html }`

## TypeScript / Vue Code Style (Frontend)

### Component Structure

All components use `<script setup lang="ts">` (Composition API only, never Options API):

```vue
<script setup lang="ts">
import type { Post } from '~/types/blog'

const props = defineProps<{ post: Post }>()

const { locale, t } = useI18n()
const localePath = useLocalePath()

const menuOpen = ref(false)
const formattedDate = computed(() => ...)

function toggleMenu() { ... }

onMounted(() => { ... })
</script>

<template>
    <!-- markup -->
</template>

<style scoped>
/* mobile-first, theme tokens only */
</style>
```

Order inside `<script setup>`: type imports, props/emits, composables, reactive state,
computed, functions, lifecycle hooks. Nuxt auto-imports (`ref`, `computed`, `useI18n`,
`onMounted`, etc.) are not explicitly imported.

### Naming

| Element        | Convention    | Example                                |
|----------------|---------------|----------------------------------------|
| Components     | `PascalCase`  | `PostCard.vue`, `NavBar.vue`           |
| Pages          | `kebab-case`  | `about-blog.vue`, `[slug].vue`         |
| Composables    | `use` prefix  | `useApi.ts`                            |
| Interfaces     | `PascalCase`  | `Post`, `TocEntry`, `PostList`         |
| CSS classes    | `kebab-case`  | `.post-preview-cover`, `.navbar-menu`  |
| Refs/variables | `camelCase`   | `menuOpen`, `currentIndex`             |

### CSS Rules

- Always `<style scoped>` -- never leak styles
- Use CSS custom properties (design tokens) exclusively: `var(--space-md)`, `var(--a-color)`
- Never hardcode colors (exception: white overlay in HeroCarousel)
- BEM-inspired flat naming: `.block-element` (no `--modifier`)
- Mobile-first responsive breakpoints: 768px (tablet), 1024px (desktop), 1200px (large)
- Accessibility: `min-height: var(--touch-target-min)` (48px), `prefers-reduced-motion`,
  `prefers-contrast: high`, focus-visible outlines
- All user-visible text uses `$t('key')` or `t('key')` -- no hardcoded strings

### Data Fetching

Use `useAsyncData` with locale-specific cache keys for page-level fetches:

```typescript
const { data } = await useAsyncData(`posts-${locale.value}`, () =>
    getPosts(locale.value, { page: page.value })
)
```

## Testing Patterns

### Backend (pytest + fakeredis)

- `conftest.py` provides an autouse `fake_redis` fixture (isolated per test)
- API tests mock the Notion client: `@patch("src.api.posts.notion_client")`
- Use `_make_page()` helper to build mock Notion page objects
- Async generators for `query_database`, `AsyncMock` for `get_blocks`
- `asyncio_mode = "auto"` -- no `@pytest.mark.asyncio` needed
- Test files: `backend/tests/test_{module}.py`, classes: `TestFeatureName`

### Frontend (vitest + @vue/test-utils)

- Use `mountSuspended` from `@nuxt/test-utils/runtime` for Nuxt-aware mounting
- Test files: `frontend/tests/components/{ComponentName}.test.ts`
- Test rendering output, CSS class presence, link hrefs, conditional visibility

## Key Rules

1. Match existing patterns -- consistency over preference
2. No unsolicited refactoring, features, or files
3. Don't create new files unless absolutely necessary
4. All i18n: links use `localePath()`, text uses `t('key')`, cache keys include locale
5. All cache keys follow `blog:{lang}:{type}:{identifier}` pattern
6. All API endpoints accept a `lang` query parameter
7. New features should include tests following existing patterns
8. If your changes affect conventions described here or in `docs/`, update the relevant
   documentation in the same commit
9. After every change, update `CHANGELOG.md` under `[Unreleased]` with what changed
