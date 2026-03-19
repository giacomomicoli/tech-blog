# Project Overview

> Authoritative reference for AI agents and developers. This document describes the current
> state of the project. All implementation decisions here are final — do not deviate from
> these patterns, naming conventions, or architectural choices.

## Identity & Branding

- **Site name**: "TECH.md"
- **Author attribution**: "FakeJack"
- **Footer text**: "© 2026 TECH.md Blog - FakeJack - Powered by Notion."
- **Default domain**: `tech.fakejack.dev`
- **SEO title**: "TECH.md" (global), appended as `{Page Title} | TECH.md` on subpages
- **Meta description**: "TECH.md — A blog powered by Notion"

These branding values are hardcoded in the frontend. Do not change them without explicit user request.

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Python + FastAPI | Python 3.12, FastAPI 0.115+ |
| HTTP client | httpx | 0.28+ |
| Frontend | Nuxt 3 (Vue 3 + TypeScript) | Nuxt 3.16+, Vue 3.5+ |
| Cache | Redis | 7 (Alpine image) |
| CMS | Notion API | v2025-09-03 |
| Reverse proxy (prod) | Traefik v3 (shared Swarm stack) | External |
| Reverse proxy (dev) | Caddy | 2 (Alpine image) |
| Container orchestration | Docker Swarm | Compose v3 |
| Backend linter | Ruff | 0.9+ |
| Backend tests | pytest + pytest-asyncio + fakeredis | |
| Frontend tests | Vitest + @vue/test-utils + happy-dom | |
| Package manager (backend) | uv | Used in Dockerfile only |
| Font | Atkinson Hyperlegible Mono | Google Fonts, monospace |

## Architecture Summary

```
┌──────────────────────────────────────────────────────────┐
│               Traefik (shared Swarm stack)                │
│      :80/:443 — auto-TLS via Let's Encrypt                │
│   Host: tech.fakejack.dev                                 │
│   /api/* /health → backend    everything else → frontend  │
└──────┬───────────────────────────────────────┬────────────┘
       │                                       │
┌──────▼──────┐                       ┌────────▼────────┐
│   Backend   │                       │    Frontend     │
│  FastAPI    │◄──── SSR fetch ───────│   Nuxt 3 SSR    │
│  :8000      │  (Docker network)     │   :3000         │
└──────┬──────┘                       └─────────────────┘
       │
┌──────▼──────┐     ┌─────────────────┐
│    Redis    │     │   Notion API    │
│   :6379     │     │ api.notion.com  │
│   cache     │     │  (external)     │
└─────────────┘     └─────────────────┘
```

- **Backend** fetches content from two Notion databases (Posts + Pages), renders Notion blocks to HTML, caches responses in Redis, and serves a REST API.
- **Frontend** is a Nuxt 3 SSR app that consumes the backend API. Server-side renders use the Docker-internal URL (`http://backend:8000`), client-side fetches use the public URL.
- **Redis** caches all API responses with a 300-second TTL. A background sync loop polls Notion every 5 minutes and invalidates stale entries.
- **Traefik** (production) is a shared reverse proxy running as a separate Swarm stack. Services connect via the `proxy-net` overlay network and expose themselves through Traefik labels.
- **Caddy** (development only) provides a local reverse proxy on `:80` for convenience.

## Notion Databases

The project uses **two separate Notion databases**, each accessed via a data source ID.

### Posts Database (`NOTION_DATA_SOURCE_ID`)

Stores blog posts. Queried via `POST /v1/data_sources/{id}/query`.

| Property | Type | Usage |
|----------|------|-------|
| Name | Title | Post title |
| Slug | Rich Text | URL identifier, must be unique |
| Excerpt | Rich Text | Card preview and meta description |
| Category | Select | One category per post (navigation grouping) |
| Tags | Multi-select | Multiple tags per post (discovery) |
| Published Date | Date | Sort order and display |
| Published | Checkbox | Only `true` posts appear on the site |
| Cover | URL | Hero image URL |
| Author | Rich Text | Author name |
| Featured | Checkbox | Shows in homepage hero carousel |
| Hero Position | Number | Position in hero section (1-5). 1 = large tile. |
| Top | Checkbox | Shows in "Top Read" sidebar (up to 3 posts) |
| Related Posts | Relation | Self-referencing relation for related posts on detail page |
| Language | Select | Language code (`it`, `en`, etc.) for multilanguage support |

### Pages Database (`NOTION_PAGES_DATA_SOURCE_ID`)

Stores static content pages (About This Blog, About Me, etc.). Queried by slug.

| Property | Type | Usage |
|----------|------|-------|
| Name | Title | Page heading |
| Slug | Rich Text | URL identifier (e.g. `about-blog`, `about-me`) |
| Language | Select | Language code (`it`, `en`, etc.) for multilanguage support |

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `NOTION_API_KEY` | Yes | — | Internal integration token (`ntn_` prefix) |
| `NOTION_DATABASE_ID` | Yes | — | Posts database UUID |
| `NOTION_DATA_SOURCE_ID` | Yes | — | Posts data source ID (v2025-09-03 query endpoint) |
| `NOTION_PAGES_DATA_SOURCE_ID` | No | `""` | Pages data source ID for static pages |
| `NOTION_API_VERSION` | No | `2025-09-03` | Notion API version header |
| `REDIS_URL` | No | `redis://redis:6379/0` | Redis connection string |
| `CACHE_TTL_SECONDS` | No | `300` | Cache entry TTL in seconds |
| `CACHE_INVALIDATE_SECRET` | Yes | — | Bearer token for `POST /api/cache/invalidate` |
| `SYNC_INTERVAL_MINUTES` | No | `5` | Background sync polling interval |
| `BACKEND_PORT` | No | `8000` | Backend service port (dev) |
| `FRONTEND_PORT` | No | `3000` | Frontend service port (dev) |
| `NUXT_PUBLIC_SITE_URL` | No | `https://tech.fakejack.dev` | Public URL for RSS/sitemap |
| `NUXT_PUBLIC_BACKEND_URL` | No | `http://localhost:8000` (dev) | Client-side API base URL |
| `NUXT_THEME` | No | `tech-dark` | Theme directory name under `assets/themes/` |
| `SUPPORTED_LOCALES` | No | `it,en` | Comma-separated list of supported locale codes |
| `DEFAULT_LOCALE` | No | `it` | Default locale for the site |

In production, sensitive variables are stored as Docker Swarm secrets at `/run/secrets/{field_name}` and take priority over environment variables.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check → `{"status": "ok"}` |
| `GET` | `/api/posts` | List published posts (params: `lang`, `tag`, `category`, `featured`, `page`, `limit`) |
| `GET` | `/api/posts/hero` | Up to 5 hero posts sorted by position (params: `lang`) |
| `GET` | `/api/posts/top` | Up to 3 top-read posts sorted by date desc (params: `lang`) |
| `GET` | `/api/posts/{slug}` | Single post with rendered HTML, TOC, reading time, related posts (params: `lang`) |
| `GET` | `/api/categories` | Sorted list of category names (params: `lang`) |
| `GET` | `/api/tags` | Sorted list of tag names (params: `lang`) |
| `GET` | `/api/pages/{slug}` | Static page by slug (params: `lang`) |
| `POST` | `/api/cache/invalidate` | Invalidate all cache (Bearer token required) |

## Frontend Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | `index.vue` | Redirects to `/{defaultLocale}` |
| `/{lang}` | `[lang]/index.vue` | Homepage with hero section + latest articles grid + top read sidebar |
| `/{lang}/blog/{slug}` | `[lang]/blog/[slug].vue` | Full post with content + TOC sidebar + related posts |
| `/{lang}/category/{name}` | `[lang]/category/[name].vue` | Posts filtered by category |
| `/{lang}/tag/{name}` | `[lang]/tag/[name].vue` | Posts filtered by tag |
| `/{lang}/about-blog` | `[lang]/about-blog.vue` | Static "About This Blog" page |
| `/{lang}/about-me` | `[lang]/about-me.vue` | Static "About Me" page |
| `/rss.xml` | Server route | RSS 2.0 feed (per-locale via `?lang=` param) |
| `/sitemap.xml` | Server route | XML sitemap (all locales with hreflang) |

## Testing

> For test counts, mock patterns, fixtures, and how to add new tests, see [`testing-and-linting.md`](testing-and-linting.md).

## Key Design Principles

1. **Notion is the CMS** — No admin panel. All content is authored in Notion. The backend only reads.
2. **Two databases, one pattern** — Posts and Pages both use data source queries. No per-page IDs in config.
3. **Server-side rendering** — Nuxt SSR for SEO. The API client switches base URLs based on context.
4. **Cache-first** — All API responses cached in Redis. Background sync invalidates stale entries.
5. **Theme system** — CSS custom properties in theme files. Selected at build time via `NUXT_THEME`.
6. **Docker Swarm for production** — Secrets, replicas, rolling updates, Traefik auto-TLS via shared reverse proxy.
7. **Monospace aesthetic** — Atkinson Hyperlegible Mono throughout. Clean, minimal design.
8. **Multilanguage support** — Content authored per-language in Notion (Language select property). URL-prefixed locales (`/it/...`, `/en/...`), translated UI via `@nuxtjs/i18n`, per-locale RSS/sitemap.
