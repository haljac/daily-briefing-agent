.PHONY: dev briefing chat format lint check fix test clean install help

# CLI Application Commands
dev: chat
	@echo "Starting interactive chat session..."

briefing:
	@echo "Getting your daily briefing..."
	uv run --package aidb-tui aidb briefing

chat:
	@echo "Starting AI Daily Briefing chat..."
	uv run --package aidb-tui aidb chat

chat-no-briefing:
	@echo "Starting chat without daily briefing..."
	uv run --package aidb-tui aidb chat --skip-briefing

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

test-cli:
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

# Package-specific development
dev-ai:
	uv run --package aidb-ai python -c "from aidb_ai.main import AIDBAgent; print('AI agent initialized successfully')"

# CLI testing and verification
cli-help:
	uv run --package aidb-tui aidb --help

cli-test: cli-help briefing

# Utilities
deps:
	uv tree

deps-outdated:
	uv pip list --outdated

help:
	@echo "AI Daily Briefing - Available Commands:"
	@echo ""
	@echo "🚀 Main Commands:"
	@echo "  make briefing        - Get daily briefing only"
	@echo "  make chat           - Interactive chat with briefing"
	@echo "  make chat-no-briefing - Interactive chat without briefing"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make install        - Install dependencies"
	@echo "  make dev            - Start development session (same as chat)"
	@echo "  make dev-ai         - Test AI agent initialization"
	@echo ""
	@echo "🧹 Code Quality:"
	@echo "  make format         - Format code with ruff"
	@echo "  make lint           - Check linting issues"
	@echo "  make check          - Run format-check and lint"
	@echo "  make fix            - Auto-fix linting and format issues"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-ai        - Test AI package"
	@echo "  make test-cli       - Test CLI package"
	@echo "  make cli-test       - Quick CLI verification"
	@echo ""
	@echo "📦 Package Management:"
	@echo "  make build          - Build packages"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make deps           - Show dependency tree"
	@echo ""
	@echo "For more info: uv run aidb --help"
