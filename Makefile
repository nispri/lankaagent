# LankaAgent — Makefile
# Common commands for development, testing, deployment

.PHONY: help up down logs shell-api shell-worker shell-mcp migrate test lint format health clean

# ─────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─────────────────────────────────────────────────────────────
# Docker Compose
# ─────────────────────────────────────────────────────────────
up: ## Start all services (dev)
	docker compose up -d --build

up-staging: ## Start staging services
	docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build

down: ## Stop all services
	docker compose down

down-volumes: ## Stop and remove volumes (DATA LOSS!)
	docker compose down -v

restart: ## Restart all services
	docker compose restart

logs: ## Follow logs for all services
	docker compose logs -f --tail=100

logs-api: ## Follow API logs
	docker compose logs -f --tail=100 api

logs-worker: ## Follow Worker logs
	docker compose logs -f --tail=100 worker

logs-mcp: ## Follow MCP logs
	docker compose logs -f --tail=100 mcp

# ─────────────────────────────────────────────────────────────
# Shell Access
# ─────────────────────────────────────────────────────────────
shell-api: ## Shell into API container
	docker compose exec api bash

shell-worker: ## Shell into Worker container
	docker compose exec worker bash

shell-mcp: ## Shell into MCP container
	docker compose exec mcp bash

shell-db: ## Shell into Postgres
	docker compose exec postgres psql -U $${POSTGRES_USER:-lankaagent} -d lankaagent

shell-redis: ## Shell into Redis
	docker compose exec redis redis-cli

# ─────────────────────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────────────────────
migrate: ## Run database migrations
	docker compose exec api alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MSG="add table")
	docker compose exec api alembic revision --autogenerate -m "$(MSG)"

migrate-downgrade: ## Downgrade one migration
	docker compose exec api alembic downgrade -1

db-seed: ## Seed database with demo data
	docker compose exec api python -m scripts.seed

db-reset: ## Reset database (DROP ALL DATA)
	docker compose exec api alembic downgrade base && make migrate && make db-seed

# ─────────────────────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────────────────────
test: ## Run all tests
	docker compose exec api pytest -v

test-unit: ## Run unit tests only
	docker compose exec api pytest -v -m "not integration"

test-integration: ## Run integration tests
	docker compose exec api pytest -v -m integration

test-cov: ## Run tests with coverage
	docker compose exec api pytest --cov=app --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	docker compose exec api pytest -v --watch

# ─────────────────────────────────────────────────────────────
# Code Quality
# ─────────────────────────────────────────────────────────────
lint: ## Run all linters
	docker compose exec api ruff check .
	docker compose exec api mypy app/

format: ## Auto-format code
	docker compose exec api ruff check --fix .
	docker compose exec api ruff format .

typecheck: ## Run mypy type checking
	docker compose exec api mypy app/

security: ## Run security scans
	docker compose exec api bandit -r app/
	docker compose exec api pip-audit

# ─────────────────────────────────────────────────────────────
# Health & Monitoring
# ─────────────────────────────────────────────────────────────
health: ## Check all service health endpoints
	@echo "Checking API..." && curl -sf http://localhost:8000/health/ready || echo "API: FAIL"
	@echo "Checking MCP..." && curl -sf http://localhost:8001/health || echo "MCP: FAIL"
	@echo "Checking Dashboard..." && curl -sf http://localhost:3000/ || echo "Dashboard: FAIL"
	@echo "Checking Grafana..." && curl -sf http://localhost:3001/api/health || echo "Grafana: FAIL"
	@echo "Checking Prometheus..." && curl -sf http://localhost:9090/-/healthy || echo "Prometheus: FAIL"

status: ## Show container status
	docker compose ps

# ─────────────────────────────────────────────────────────────
# MCP Tools
# ─────────────────────────────────────────────────────────────
mcp-call: ## Call MCP tool (usage: make mcp-call TOOL=search_attractions ARGS='{"province": "Southern"}')
	docker compose exec mcp python -m mcp_client call $(TOOL) '$(ARGS)'

mcp-list: ## List available MCP tools
	docker compose exec mcp python -m mcp_client list

# ─────────────────────────────────────────────────────────────
# Development Utilities
# ─────────────────────────────────────────────────────────────
install-pre-commit: ## Install pre-commit hooks locally
	pip install pre-commit && pre-commit install

update-deps: ## Update Python dependencies
	docker compose exec api poetry update
	docker compose exec worker poetry update
	docker compose exec mcp poetry update

generate-openapi: ## Generate OpenAPI spec
	docker compose exec api python -c "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json

# ─────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────
clean: ## Remove all containers, networks, volumes
	docker compose down -v --remove-orphans
	docker system prune -f

clean-all: ## Nuclear cleanup (includes images)
	docker compose down -v --remove-orphans
	docker system prune -af --volumes

# ─────────────────────────────────────────────────────────────
# Deployment
# ─────────────────────────────────────────────────────────────
deploy-staging: ## Deploy to staging (Railway)
	railway up --detach

deploy-prod: ## Deploy to production (requires approval)
	gh workflow run deploy-prod.yml -f environment=production

# ─────────────────────────────────────────────────────────────
# Default
# ─────────────────────────────────────────────────────────────
.DEFAULT_GOAL := help