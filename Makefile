.PHONY: help build up down restart logs test lint format clean shell db-shell setup

# Variables
DOCKER_COMPOSE = docker-compose
BACKEND_CONTAINER = backend

help: ## Show this help message
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build docker images
	$(DOCKER_COMPOSE) build

up: ## Start all services in the background
	$(DOCKER_COMPOSE) up -d

down: ## Stop all services and remove containers
	$(DOCKER_COMPOSE) down

restart: ## Restart all services
	$(DOCKER_COMPOSE) restart

logs: ## Tail logs for all services
	$(DOCKER_COMPOSE) logs -f

test: ## Run backend tests
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) pytest

lint: ## Run pre-commit hooks on all files
	pre-commit run --all-files

format: ## Format Python code with black and isort
	black backend/
	isort backend/

clean: ## Remove pycache and pytest cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

shell: ## Open a shell inside the backend container
	$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) /bin/bash

db-shell: ## Open a psql shell
	$(DOCKER_COMPOSE) exec db psql -U postgres -d vas_db

setup: ## Install pre-commit hooks and local dev dependencies
	pip install -e "backend/[dev]"
	pre-commit install
