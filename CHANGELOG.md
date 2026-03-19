# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-03-20

### Added

#### Backend (Python / FastAPI)

- Notion-powered CMS with async API client targeting Notion API v2025-09-03
- REST API endpoints: post listing with pagination/filtering, single post retrieval,
  categories, tags, static pages, hero posts, top posts, cache invalidation, and health check
- Notion-to-HTML renderer supporting 20+ block types with rich text formatting
- Table of contents extraction and reading time estimation
- Redis cache layer with cache-first pattern, structured keys (`blog:{lang}:{type}:{id}`),
  configurable TTL, and pattern-based invalidation
- Background sync loop polling Notion for recently edited posts and auto-invalidating cache
- Token-bucket rate limiter with exponential backoff and retry on 429 responses
- Dual Notion database support for blog posts and static pages
- Pydantic Settings configuration with `.env` and Docker Secrets support
- Multi-locale support with configurable `SUPPORTED_LOCALES` and `DEFAULT_LOCALE`
- pytest test suite with fakeredis isolation and mocked Notion client

#### Frontend (Nuxt 3 / Vue 3 / TypeScript)

- Pages: home (hero carousel + post grid), post detail, category listing, tag listing,
  about-blog, about-me
- Components: HeroCarousel, NavBar, PostCard, PostMeta, TableOfContents
- Centralized API composable (`useApi`) with SSR-aware base URL switching
- Internationalization (Italian + English) via `@nuxtjs/i18n` with prefix-based URL strategy
- CSS custom properties design token system with switchable themes (`tech-dark`, `tech-light`,
  `yarb-dark`, `yarb-light`)
- Dynamic SEO meta tags (Open Graph, Twitter Card) per post
- Mobile-first responsive design with page transitions and monospace typography
- RSS 2.0 feed and XML sitemap server routes
- Vitest component tests using `@nuxt/test-utils`

#### Infrastructure

- Docker three-service architecture: backend, frontend, Redis
- Dev environment with Caddy reverse proxy, hot-reload volume mounts
- Production environment with Traefik reverse proxy (shared Swarm stack), HTTPS
  (Let's Encrypt), Docker Swarm deployment, resource limits, and rolling updates
- Namespaced Docker Swarm secrets (`techblog_*`) with source/target mapping
- GitHub Actions CI workflow: lint (ruff), backend tests (pytest), frontend tests (vitest)
  on push/PR to dev, release, main
- GitHub Actions Deploy workflow: build and push Docker images to ghcr.io, deploy to VPS
  via SSH on push to main
- Docker images published to GitHub Container Registry (ghcr.io) with commit SHA tags
- Manual/emergency deploy script with Docker Secrets management
- Makefile for all build, test, lint, and deploy operations

#### Documentation

- Project overview with architecture diagram, tech stack, Notion schemas, environment
  variables, API endpoints, and frontend routes
- Backend architecture reference (Notion client, API endpoints, cache layer, renderer)
- Frontend architecture reference (components, pages, composables, theme system)
- Coding standards (Python, TypeScript, CSS conventions, i18n, API contract)
- Docker and deployment reference (compose files, Traefik, CI/CD, server architecture)
- Testing and linting reference (pytest, vitest, ruff configuration)
- Notion setup guide (database properties, setup steps)
- AGENTS.md as sole entry point for AI coding agents
