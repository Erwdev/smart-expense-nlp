# ==============================================================================
# Makefile for Smart Expense NLP
# ==============================================================================

POETRY_RUN = poetry run

# Mark all targets as phony so make tidak mengira ini nama file
.PHONY: setup run-api test format lint \
	docker-build docker-up docker-up-dev docker-down docker-logs docker-test \
	clean clean-all lock update shell export-requirements check-deps outdated

# Target to set up the development environment.
setup:
	@echo "--> Installing all dependencies (main, dev, training)..."
	@poetry install --no-root


# Run FastAPI
run-api:
	@echo "--> Starting FastAPI server at http://127.0.0.1:8000"
	@$(POETRY_RUN) uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload

# Test
test:
	@echo "--> Running tests..."
	@$(POETRY_RUN) pytest

# Format
format:
	@echo "--> Formatting code with black..."
	@$(POETRY_RUN) black .

# Lint
lint:
	@echo "--> Checking code quality with ruff..."
	@$(POETRY_RUN) ruff check .

# ----------------- Docker -----------------
docker-build: ## Build Docker image
	 docker build -t smart-expense-nlp:latest .

docker-up: ## Start Docker Compose services
	 docker-compose up -d

docker-up-dev: ## Start Docker Compose with Jupyter notebook
	 docker-compose --profile dev up -d

docker-down: ## Stop Docker Compose services
	 docker-compose down

docker-logs: ## Show Docker Compose logs
	 docker-compose logs -f api

docker-test: ## Test Docker container
	 docker run -d -p 8000:8000 --name test-api smart-expense-nlp:latest
	 @sleep 10
	 curl -f http://localhost:8000/health || (docker stop test-api && docker rm test-api && exit 1)
	 docker stop test-api
	 docker rm test-api

# ----------------- Cleanup & deps -----------------
clean: ## Clean up generated files and caches
	 find . -type d -name "__pycache__" -exec rm -rf {} +
	 find . -type d -name "*.egg-info" -exec rm -rf {} +
	 find . -type d -name ".pytest_cache" -exec rm -rf {} +
	 find . -type d -name ".ruff_cache" -exec rm -rf {} +
	 find . -type d -name ".mypy_cache" -exec rm -rf {} +
	 find . -type f -name "*.pyc" -delete
	 find . -type f -name "*.pyo" -delete
	 find . -type f -name ".coverage" -delete
	 rm -rf htmlcov/
	 rm -rf dist/
	 rm -rf build/

clean-all: clean ## Clean everything including poetry env
	 poetry env remove --all

lock: ## Update poetry.lock file
	 poetry lock --no-update

update: ## Update dependencies to latest versions
	 poetry update

shell: ## Activate Poetry shell
	 poetry shell

export-requirements: ## Export requirements.txt from Poetry (for compatibility)
	 poetry export -f requirements.txt --output requirements.txt --without-hashes
	 poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
	 poetry export -f requirements.txt --output requirements-training.txt --with training --without-hashes

check-deps: ## Check for dependency issues
	 poetry check
	 poetry show --tree

outdated: ## Show outdated dependencies
	 poetry show --outdated
