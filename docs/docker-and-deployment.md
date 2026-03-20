# Docker & Deployment

> Authoritative reference for AI agents and developers. This document describes the current
> Docker orchestration, service configuration, and deployment procedures. Do not deviate
> from these patterns when making infrastructure changes.

## File Layout

```
docker/
├── docker-compose.yml       # Base service definitions (shared dev + prod)
├── docker-compose.dev.yml   # Dev overrides: Caddy proxy, hot reload, bridge network, no persistence
├── docker-compose.prod.yml  # Prod overrides: Traefik labels, secrets, resource limits
├── Caddyfile                # Dev reverse proxy routing and security headers
└── deploy.sh                # Manual/emergency deployment script (secrets + Swarm stack)

backend/
├── Dockerfile               # Python 3.12-slim, multi-stage with uv
└── ...

frontend/
├── Dockerfile               # Node 20 Alpine, 3-stage build
├── docker-entrypoint.dev.sh # Dev: npm install before starting Nuxt dev server
└── ...

Makefile                     # All build, test, and deploy commands
.env.example                 # Template for required environment variables
```

## Services

### Base Services (`docker-compose.yml`)

All three core services are defined here. Dev and prod overlays modify them.

#### backend

- **Image**: `ghcr.io/giacomomicoli/tech-blog/backend:${IMAGE_TAG:-latest}`
- **Build**: `../backend` with `Dockerfile`
- **Port**: `${BACKEND_PORT:-8000}:8000`
- **Env**: Loaded from `../.env`
- **Network**: `blog-net`
- **Health check**: `curl -f http://localhost:8000/health` — 30s interval, 5s timeout, 3 retries, 10s start period

#### frontend

- **Image**: `ghcr.io/giacomomicoli/tech-blog/frontend:${IMAGE_TAG:-latest}`
- **Build**: `../frontend` with `Dockerfile`
- **Build arg**: `NUXT_THEME=${NUXT_THEME:-tech-dark}` (theme baked at build time)
- **Port**: `${FRONTEND_PORT:-3000}:3000`
- **Environment**:
  - `BACKEND_URL=http://backend:8000` (server-side, Docker network)
  - Plus `.env` file
- **Network**: `blog-net`
- **Health check**: `curl -f http://localhost:3000/` — 30s interval, 5s timeout, 3 retries, 15s start period

#### redis

- **Image**: `redis:7-alpine`
- **Port**: `6379:6379`
- **Network**: `blog-net`
- **Health check**: `redis-cli ping` — 10s interval, 3s timeout, 3 retries

### Network

- **Name**: `blog-net`
- **Base driver**: `overlay` (attachable)
- **Dev override**: `bridge` (Swarm not required for dev)

## Development Environment (`docker-compose.dev.yml`)

Overrides for local development with hot reload. Adds Caddy as a local reverse proxy.

### caddy (dev only)

- **Image**: `caddy:2-alpine`
- **Port**: `${CADDY_PORT:-80}:80` (HTTP only, no TLS)
- **Volume**: `./Caddyfile:/etc/caddy/Caddyfile:ro`
- **Depends on**: `frontend`, `backend`
- **Routing**: `/api/*` and `/health` → backend:8000, everything else → frontend:3000

### backend

- **Depends on**: `redis` (healthy)
- **Volume**: `../backend:/app` (live source code mount)
- **Command**: `uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload`

### frontend

- **Depends on**: `backend` (healthy)
- **Volumes**:
  - `../frontend:/app` (live source code mount)
  - `/app/node_modules` (anonymous volume — prevents host node_modules from overwriting container's)
  - `/app/.nuxt` (anonymous volume — build cache)
- **Environment**:
  - `NUXT_THEME=${NUXT_THEME:-tech-dark}` (runtime for dev, unlike build-time in prod)
  - `NUXT_PUBLIC_BACKEND_URL=http://localhost:8000` (client-side API URL for dev)
- **Entrypoint**: `/app/docker-entrypoint.dev.sh` (runs `npm install` first, then `exec "$@"`)
- **Command**: `npx nuxt dev --host 0.0.0.0`

### redis

- **Command**: `redis-server --save "" --appendonly no` (in-memory only, no persistence)

### Network

- **Driver**: `bridge` (overrides overlay, no Swarm needed)

## Production Environment (`docker-compose.prod.yml`)

Production uses a shared Traefik reverse proxy (deployed separately as a Swarm stack).
Traefik discovers blog services via `deploy.labels` (Swarm provider). No Caddy in production.

### Reverse Proxy: Traefik (external)

Traefik runs as a separate shared Swarm stack at `/var/www/traefik/` on the server. It is
**not** part of the tech blog compose files. Blog services connect to the shared `proxy-net`
overlay network and declare Traefik routing rules via `deploy.labels`.

Routing rules:
- `Host(tech.fakejack.dev) && (PathPrefix(/api) || Path(/health))` → backend:8000
- `Host(tech.fakejack.dev)` (priority 1, catch-all) → frontend:3000

Middlewares (defined in frontend labels, referenced by both routers):
- `techblog-headers`: Security headers (nosniff, deny framing, strict referrer)
- `techblog-compress`: gzip/brotli compression

### backend (overrides)

- **Ports**: Removed (only accessible via Traefik)
- **env_file**: Removed (secrets used instead)
- **Environment**: `REDIS_URL=redis://redis:6379/0`, `NOTION_API_VERSION=2025-09-03`
- **Networks**: Added `proxy-net` (for Traefik discovery)
- **Secrets** (namespaced with `techblog_` prefix, mapped to `/run/secrets/{name}`):
  - `techblog_notion_api_key` → `notion_api_key`
  - `techblog_notion_database_id` → `notion_database_id`
  - `techblog_notion_data_source_id` → `notion_data_source_id`
  - `techblog_notion_pages_data_source_id` → `notion_pages_data_source_id`
  - `techblog_cache_invalidate_secret` → `cache_invalidate_secret`
- **Deploy**: 1 replica, rolling update (parallelism 1, 10s delay), restart on-failure (max 3), memory limit 256M
- **Traefik labels**: `techblog-api` router on HTTPS entrypoint with TLS cert resolver

### frontend (overrides)

- **Ports**: Removed
- **env_file**: Removed
- **Environment**:
  - `BACKEND_URL=http://backend:8000` (server-side, unchanged)
  - `NUXT_PUBLIC_SITE_URL=${NUXT_PUBLIC_SITE_URL:-https://tech.fakejack.dev}`
- **Networks**: Added `proxy-net` (for Traefik discovery)
- **Deploy**: 1 replica, rolling update (parallelism 1, 10s delay), restart on-failure (max 3), memory limit 256M
- **Traefik labels**: `techblog` router (catch-all, priority 1) on HTTPS entrypoint with TLS cert resolver, security headers and compression middlewares

### redis (overrides)

- **Ports**: Removed
- **Volume**: `redis-data:/data` (persistent storage)
- **Command**: `redis-server --appendonly yes` (AOF persistence enabled)
- **Deploy**: 1 replica, restart on-failure (max 3), memory limit 128M

### Secrets

Docker Swarm secrets are globally scoped. The tech blog uses a `techblog_` prefix to avoid
collision with the gaming blog's secrets. The `source`/`target` syntax in the compose file
maps the namespaced Docker secret to the expected path inside the container.

| Docker Secret Name | Mounted As | Source Env Var |
|--------------------|-----------|---------------|
| `techblog_notion_api_key` | `/run/secrets/notion_api_key` | `NOTION_API_KEY` |
| `techblog_notion_database_id` | `/run/secrets/notion_database_id` | `NOTION_DATABASE_ID` |
| `techblog_notion_data_source_id` | `/run/secrets/notion_data_source_id` | `NOTION_DATA_SOURCE_ID` |
| `techblog_notion_pages_data_source_id` | `/run/secrets/notion_pages_data_source_id` | `NOTION_PAGES_DATA_SOURCE_ID` |
| `techblog_cache_invalidate_secret` | `/run/secrets/cache_invalidate_secret` | `CACHE_INVALIDATE_SECRET` |

The backend's `config.py` reads secrets from `/run/secrets/` in `model_post_init` and they
override env var values.

### Named Volumes

| Volume | Service | Purpose |
|--------|---------|---------|
| `redis-data` | redis | Persistent Redis data (AOF) |

### Networks

| Network | Driver | Purpose |
|---------|--------|---------|
| `blog-net` | overlay | Internal: backend ↔ redis communication |
| `proxy-net` | overlay (external) | Shared: Traefik ↔ blog services |

## Caddyfile (Dev Only)

```
:80 {
    encode gzip zstd

    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }

    handle /api/* {
        reverse_proxy backend:8000
    }
    handle /health {
        reverse_proxy backend:8000
    }
    handle {
        reverse_proxy frontend:3000
    }

    log { output stdout; format console }
}
```

- Listens on HTTP port 80 (no TLS for local dev)
- Compression: gzip + zstd
- Security headers: nosniff, deny framing, strict referrer, no server header
- Routing: `/api/*` and `/health` → backend:8000, everything else → frontend:3000

## CI/CD Pipeline

Production deployments are automated via GitHub Actions. Two workflows live in `.github/workflows/`:

### CI Workflow (`ci.yml`)

Runs on every push and pull request to `dev`, `release`, and `main`. Three parallel jobs:

| Job | Runner | Steps |
|-----|--------|-------|
| **lint** | Python 3.12 | `ruff check src/` + `ruff format --check src/` |
| **test-backend** | Python 3.12 + uv | `uv pip install --system ".[dev]"` then `pytest tests/ -v` |
| **test-frontend** | Node 20 | `npm ci` then `npx vitest run` |

No Docker containers or service dependencies needed — backend tests use `fakeredis` (in-process),
frontend tests use `happy-dom`.

### Deploy Workflow (`deploy.yml`)

Runs on push to `main` only. Two sequential jobs:

**Job 1: `build-and-push`**
1. Checks out the repository
2. Sets up Docker Buildx
3. Logs in to ghcr.io using the automatic `GITHUB_TOKEN`
4. Builds and pushes backend image with tags `latest` + git SHA
5. Builds and pushes frontend image with tags `latest` + git SHA
6. Uses GitHub Actions cache (`type=gha`) for Docker layer caching

**Job 2: `deploy`** (depends on `build-and-push`)
1. SSHs into the VPS using `appleboy/ssh-action`
2. Logs in to ghcr.io on the VPS (using forwarded `GITHUB_TOKEN`)
3. Pulls latest code: `git fetch origin main && git reset --hard origin/main`
4. Deploys stack with `IMAGE_TAG` set to the git SHA:
   `docker stack deploy --with-registry-auth -c docker-compose.yml -c docker-compose.prod.yml techblog`

### Container Registry

Images are stored in GitHub Container Registry (ghcr.io):

| Image | URL |
|-------|-----|
| Backend | `ghcr.io/giacomomicoli/tech-blog/backend` |
| Frontend | `ghcr.io/giacomomicoli/tech-blog/frontend` |

Each image is tagged with both `latest` and the full git commit SHA for traceability.
The base compose file uses `${IMAGE_TAG:-latest}` so local dev defaults to `latest`
while CI deploys use the exact commit SHA.

### Required GitHub Secrets

Configure these in the repository settings before the first deploy:

| Secret | Value |
|--------|-------|
| `VPS_SSH_KEY` | SSH private key for the VPS |
| `VPS_HOST` | VPS IP address (`91.99.20.92`) |
| `VPS_USER` | SSH user (`fakejack`) |

`GITHUB_TOKEN` is provided automatically by GitHub Actions — no PAT required.

## Deployment Script (`deploy.sh`)

Manual / emergency deploy script. Normal deploys go through the CI/CD pipeline above.

```bash
#!/usr/bin/env bash
set -euo pipefail
```

1. Sources `../.env` file (exits with error if missing)
2. For each secret (`notion_api_key`, `notion_database_id`, `notion_data_source_id`,
   `notion_pages_data_source_id`, `cache_invalidate_secret`):
   - Converts lowercase name to uppercase env var
   - Skips with warning if value is empty
   - Removes existing `techblog_` prefixed secret (`docker secret rm`, ignores errors)
   - Creates new secret: `echo "$value" | docker secret create "techblog_$secret" -`
3. Deploys stack: `docker stack deploy --with-registry-auth -c docker-compose.yml -c docker-compose.prod.yml techblog`

Docker secrets are immutable — the script removes and recreates them on each deploy.

## Dockerfiles

### Backend (`backend/Dockerfile`)

Two-stage build:

1. **builder**: `python:3.12-slim`
   - Installs `uv` (fast pip replacement)
   - Copies `pyproject.toml`, installs dependencies with `uv pip install --system --no-cache`
2. **runtime**: `python:3.12-slim`
   - Copies installed packages and uvicorn from builder
   - Installs `curl` (for health checks)
   - Copies application code
   - Exposes port 8000
   - CMD: `uvicorn src.main:app --host 0.0.0.0 --port 8000`

### Frontend (`frontend/Dockerfile`)

Three-stage build:

1. **deps**: `node:20-alpine`
   - Copies `package.json` + `package-lock.json`, runs `npm install`
2. **builder**: `node:20-alpine`
   - Receives `NUXT_THEME` build arg (default: `tech-dark`)
   - Copies node_modules from deps, copies source, runs `npm run build`
3. **runtime**: `node:20-alpine`
   - Installs `curl` (for health checks)
   - Copies `.output/` from builder
   - Sets `HOST=0.0.0.0`, `PORT=3000`
   - CMD: `node .output/server/index.mjs`

The theme is baked into the build — changing the theme requires a rebuild.

## Makefile

All operations run from the project root.

### Variables

```makefile
COMPOSE_DEV = cd docker && docker compose -f docker-compose.yml -f docker-compose.dev.yml
```

### Targets

| Target | Command | Description |
|--------|---------|-------------|
| `dev` | `$(COMPOSE_DEV) up -d --build` | Start dev with hot reload + Caddy proxy |
| `dev-down` | `$(COMPOSE_DEV) down` | Stop dev containers |
| `dev-rebuild` | `$(COMPOSE_DEV) down -v && $(COMPOSE_DEV) up -d --build` | Full rebuild, clears volumes |
| `prod-deploy` | `cd docker && bash deploy.sh` | Create secrets + deploy Swarm stack |
| `prod-down` | `docker stack rm techblog` | Remove Swarm stack |
| `logs` | `$(COMPOSE_DEV) logs -f` | Follow all service logs |
| `logs-backend` | `$(COMPOSE_DEV) logs -f backend` | Follow backend logs |
| `logs-frontend` | `$(COMPOSE_DEV) logs -f frontend` | Follow frontend logs |
| `backend-shell` | `$(COMPOSE_DEV) exec backend bash` | Shell into backend container |
| `frontend-shell` | `$(COMPOSE_DEV) exec frontend sh` | Shell into frontend container |
| `cache-bust` | `curl -s -X POST ... \| python3 -m json.tool` | POST to cache invalidate endpoint |
| `test` | `test-backend` + `test-frontend` | Run all tests |
| `test-backend` | `$(COMPOSE_DEV) exec backend python -m pytest tests/ -v` | Run pytest inside Docker |
| `test-frontend` | `$(COMPOSE_DEV) exec frontend npx vitest run` | Run vitest inside Docker |
| `lint` | `cd backend && uvx ruff check src/ && uvx ruff format --check src/` | Lint + format check |

### Running a Single Test

```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
    exec backend pytest tests/test_renderer.py::test_function_name -v
```

## Resource Limits (Production)

| Service | Memory | Replicas |
|---------|--------|----------|
| Backend | 256M | 1 |
| Frontend | 256M | 1 |
| Redis | 128M | 1 |

Total blog footprint: ~640M. Traefik is shared across all services on the server.

## Server Architecture

The VPS runs Docker Swarm with a shared Traefik instance that routes traffic to multiple
projects. Each project deploys as its own Swarm stack connecting to the shared `proxy-net`
overlay network.

```
Internet
  │
  ▼
Traefik (shared Swarm stack, /var/www/traefik/)
  ├── opencloud.fakejack.dev  → OpenCloud (docker compose)
  ├── gaming.fakejack.dev     → Gaming Blog (Swarm stack "blog")
  ├── tech.fakejack.dev       → Tech Blog (Swarm stack "techblog")
  └── traefik-opencloud.fakejack.dev → Traefik Dashboard
```

- **Traefik** uses both `providers.swarm` (for Swarm stacks) and `providers.docker` (for
  compose containers like OpenCloud) with `exposedByDefault=false`.
- **proxy-net**: Shared overlay network (attachable) connecting Traefik to all services.
- Each project manages its own internal network for inter-service communication.
- TLS certificates are automatically obtained via Let's Encrypt (ACME HTTP challenge).

## Dev vs Prod Summary

| Aspect | Development | Production |
|--------|-------------|------------|
| Network driver | bridge | overlay (Swarm) |
| Reverse proxy | Caddy (localhost:80) | Traefik (shared, ports 80/443) |
| Ports exposed | Caddy:80, backend:8000, frontend:3000, redis:6379 | Traefik only (external) |
| Redis persistence | Off (in-memory) | AOF enabled |
| Hot reload | Yes (volume mounts) | No (built into image) |
| Secrets | `.env` file | Docker Swarm secrets (`techblog_*` prefix) |
| Replicas | 1 each | 1 each |
| TLS | None | Auto via Traefik/Let's Encrypt |
| Client API URL | `http://localhost:8000` | Not set (Traefik proxies `/api/*`) |
| Theme loading | Runtime env var | Build-time arg |
