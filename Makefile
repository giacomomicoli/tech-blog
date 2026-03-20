COMPOSE_DEV = cd docker && docker compose -f docker-compose.yml -f docker-compose.dev.yml

.PHONY: dev dev-down dev-rebuild prod-deploy prod-down logs logs-backend logs-frontend backend-shell frontend-shell cache-bust lint test test-backend test-frontend

# ── Development ──────────────────────────────────────────────

dev:
	$(COMPOSE_DEV) up -d --build

dev-down:
	$(COMPOSE_DEV) down

dev-rebuild:
	$(COMPOSE_DEV) down -v
	$(COMPOSE_DEV) up -d --build

# ── Production ───────────────────────────────────────────────

prod-deploy:
	cd docker && bash deploy.sh

prod-down:
	docker stack rm techblog

# ── Logs ─────────────────────────────────────────────────────

logs:
	$(COMPOSE_DEV) logs -f

logs-backend:
	$(COMPOSE_DEV) logs -f backend

logs-frontend:
	$(COMPOSE_DEV) logs -f frontend

# ── Shell access ─────────────────────────────────────────────

backend-shell:
	$(COMPOSE_DEV) exec backend bash

frontend-shell:
	$(COMPOSE_DEV) exec frontend sh

# ── Utilities ────────────────────────────────────────────────

cache-bust:
	@echo "Invalidating all cache..."
	@curl -s -X POST http://localhost:8000/api/cache/invalidate \
		-H "Authorization: Bearer $$(grep CACHE_INVALIDATE_SECRET .env | cut -d= -f2)" | python3 -m json.tool

lint:
	cd backend && uvx ruff check src/
	cd backend && uvx ruff format --check src/

test: test-backend test-frontend

test-backend:
	$(COMPOSE_DEV) exec backend python -m pytest tests/ -v

test-frontend:
	$(COMPOSE_DEV) exec frontend npx vitest run
