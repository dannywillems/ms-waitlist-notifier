.PHONY: help
help: ## Ask for help!
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup: ## Setup development environment
	uv sync

.PHONY: check
check: lint typecheck test ## Run all checks (lint, typecheck, test)

.PHONY: lint
lint: ## Run ruff linter
	uv run ruff check src tests

.PHONY: lint-docker
lint-docker: ## Lint Dockerfile using hadolint
	hadolint Dockerfile

.PHONY: lint-shell
lint-shell: ## Lint shell scripts using shellcheck
	shellcheck .github/scripts/*.sh

.PHONY: check-format
check-format: ## Check code formatting
	uv run ruff format --check src tests

.PHONY: format
format: ## Format code
	uv run ruff format src tests
	uv run ruff check --fix src tests

.PHONY: typecheck
typecheck: ## Run mypy type checker
	uv run mypy src tests

.PHONY: test
test: ## Run tests
	uv run pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage
	uv run pytest --cov=notifier --cov-report=html

.PHONY: clean
clean: ## Clean build artifacts
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	find . -type d -name "__pycache__" \
		-exec rm -rf {} + 2>/dev/null || true

.PHONY: docker-build
docker-build: ## Build Docker image
	docker build -t ms-waitlist-notifier:latest .

.PHONY: docker-build-amd64
docker-build-amd64: ## Build Docker image for linux/amd64
	docker build --platform linux/amd64 \
		-t ms-waitlist-notifier:latest-amd64 .
