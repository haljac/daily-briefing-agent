.PHONY: dev format lint check fix test clean install

# Development
dev:
	uv run --package aidb-tui aidb

install:
	uv sync

# Code quality
format:
	uv run ruff format .

lint:
	uv run ruff check .

check: format-check lint

format-check:
	uv run ruff format --check .

fix: lint-fix format

lint-fix:
	uv run ruff check --fix .

# Testing
test:
	uv run pytest

test-ai:
	uv run pytest packages/aidb-ai/tests/

test-tui:
	uv run pytest packages/aidb-tui/tests/

# Package operations
build:
	uv build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

# Package-specific commands
dev-ai:
	uv run --package aidb-ai python -m aidb_ai.main

dev-tui:
	uv run --package aidb-tui aidb

# Utilities
deps:
	uv tree

deps-outdated:
	uv pip list --outdated
