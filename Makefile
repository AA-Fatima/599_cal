.PHONY: help up down build logs ingest clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all services with docker-compose
	docker-compose up -d

down: ## Stop all services
	docker-compose down

build: ## Build all Docker images
	docker-compose build

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs only
	docker-compose logs -f backend

logs-frontend: ## View frontend logs only
	docker-compose logs -f frontend

ingest: ## Run data ingestion script
	docker-compose exec backend python scripts/ingest_data.py

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U calories -d calories

clean: ## Stop services and remove volumes
	docker-compose down -v

restart: down up ## Restart all services

rebuild: down build up ## Rebuild and restart all services
