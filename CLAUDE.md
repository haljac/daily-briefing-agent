# AI Daily Summary Bot Development Framework for Claude

## Project Overview

**[ai-daily-briefing]** ([AIDB]) is a TUI-driven chat bot that starts the session my providing a daily brifing that performs two actions.
1. Fetches weather information pertaining to the user's locale.
2. Provides the top news headlines with brief summaries of each story.

It then accepts further input from the user, using the weather and news tools available to answer follow up questions if necessary.

This project uses gemini-2.5-flash as well as Pydantic AI framework. The TUI is driven by Textual.

### Core Mission
- **Input**: Free-form user querires as a follow-up to the daily briefing, which is presented at the start of each session.
- **Process**: Tool calls and processing by gemini-2.5-flash
- **Output**: A daily briefing plus responses from the LLM regarding follow up questions or additional requests.

## Architecture Principles

### 1. **uv Workspace Structure**
- **aidb-ai**: Interface models defining the REST API surface (Pydantic models only)
- **aidb-tui**: Terminal interface for interactive analysis and commands (optional)
- **Modular Separation**: Clean boundaries between interface definitions and implementation details

### 2. **Modular Monolith Design**
- **Pydantic AI Application** - HTTP interface and request handling (`[project]_api.main`)
- **Provider Pattern** - Dependency injection system for clean separation of concerns (`[project]_api.providers`)
- **v1 API Endpoints** - Versioned API structure under `/v1/` prefix (`endpoints/v1/`)
- **Task Queue** - Sequential processing to prevent rate limiting (`lib/queue/`)
- **SQLite Task Manager** - Persistent storage without external dependencies (`lib/models/`)
- **Business Services** - Core business logic and external integrations (`services/`)
- **Database Integration** - Connection to existing databases or data sources (`lib/sql/`)

### 3. **Service-Oriented Processing**
- **Individual Service Sessions**: Each unit of work gets dedicated processing (avoids context issues)
- **Standardized Categories**: Predefined classification system ensures consistent categorization
- **Intelligent Aggregation**: Groups related items and generates actionable insights
- **Rate Limiting**: Conservative approach to avoid quota exhaustion

### 4. **Scalability Patterns**
- **Sequential Task Execution**: One task at a time with concurrent processing within tasks
- **Async Everything**: FastAPI + async/await throughout the stack
- **Provider Pattern**: Clean dependency injection with built-in transaction management
- **Container Ready**: Docker + docker-compose deployment

## Key Components

### **uv Workspace Layout** (`pyproject.toml`)
```
[project]/ (workspace root)
├── packages/
│   ├── [project]-core/          # Interface models only
│   │   └── src/[project]_core/
│   │       ├── models/          # Core interface models
│   │       └── settings.py      # Shared configuration
│   ├── [project]-api/           # Complete implementation
│   │   └── src/[project]_api/
│   │       ├── main.py          # FastAPI application
│   │       ├── providers.py     # Provider pattern dependency injection
│   │       ├── endpoints/       # API endpoints
│   │       │   └── v1/          # v1 API endpoints
│   │       ├── lib/             # Implementation library
│   │       │   ├── analysis/    # Business logic, categorization
│   │       │   ├── logs/        # Log extraction and processing
│   │       │   ├── models/      # SQLite models, task manager
│   │       │   ├── parsers/     # Data parsers and formatters
│   │       │   ├── queue/       # Task queue management
│   │       │   ├── sql/         # Database models and session
│   │       │   └── utils/       # Rate limiter, API utilities
│   │       ├── models/          # API request/response models
│   │       └── services/        # Business logic services
│   └── [project]-tui/           # Terminal interface (optional)
│       └── src/[project]_tui/
│           └── main.py          # CLI commands
├── scripts/                     # Utility scripts
└── tests/                       # Workspace-level integration tests
```

### **API Layer** (`[project]_api/main.py`)
- **FastAPI application** with Pydantic models
- **v1 API Structure**: All endpoints under `/v1/` prefix for versioning
- **Standard Endpoints**: `/v1/tasks`, `/v1/tasks/{id}`, `/v1/tasks/{id}/results`, `/health`, `/v1/queue/status`
- **Error Handling**: HTTP status codes with detailed error messages
- **Validation**: Request/response validation via Pydantic

### **Provider Pattern** (`[project]_api/providers.py`)
- **Dependency Injection**: Clean separation of concerns with FastAPI's Depends system
- **Database Sessions**: Enhanced with built-in transaction management
- **Service Providers**: Centralized creation and configuration of services
- **Transaction Support**: Automatic commit/rollback with `async with session:` pattern
- **Testability**: Easy mocking and overriding for unit tests

### **Task Management** (`lib/models/task_manager.py`, `lib/models/sqlite_models.py`)
- **SQLite persistence** for task state and results
- **Task lifecycle**: pending → processing → completed/failed
- **Progress tracking** with work unit counts and queue positions
- **Result storage** with JSON output

### **Business Services** (`services/`)
- **Core Service** (`core_service.py`): Main business logic processing
- **Aggregation Service** (`aggregation_service.py`): Combines results into comprehensive reports
- **Task Orchestrator** (`task_orchestrator.py`): Workflow management and coordination

### **Infrastructure** (`lib/`)
- **Task Queue** (`queue/task_queue.py`): Sequential processing with queue position tracking
- **Rate Limiter** (`utils/rate_limiter.py`): API quota management with exponential backoff
- **Data Extractor** (`logs/data_extractor.py`): Intelligent data parsing and extraction
- **Classification System** (`analysis/categories.py`): Standardized categorization with fuzzy matching
- **Analysis Engine** (`analysis/analysis_engine.py`): Pattern detection and data insights

## Development Guidelines

### **uv Workspace Commands**
```bash
# Install entire workspace
uv sync

# Start development server  
make dev                    # Uses [project]_api.main:app

# Code quality (REQUIRED after changes)
make format                 # Format code with ruff
make lint                   # Run linting checks
make check                  # Combined format-check + lint (CI mode)
make fix                    # Auto-fix all issues + format

# Run tests (run tests frequently as you make changes and in-between logical groups of changes to ensure validity).
make test                   # All tests (unit + integration)
make test-unit             # Unit tests only
make test-integration      # Integration tests (requires container)
make test-api              # API layer tests
make test-core             # Core package tests

# Container operations
make up                    # Start with docker-compose
make down                  # Stop containers
```

### **Code Patterns**
- **Async/Await**: All I/O operations are async
- **Pydantic Models**: Type-safe data validation and serialization
- **Provider Pattern**: Clean dependency injection with `Depends(get_service)`
- **Transaction Management**: Use `async with session:` for ACID operations
- **Error Propagation**: Domain-specific errors with HTTP mapping
- **Logging**: Structured logging with appropriate levels. Don't use print statements -- use the logger defined in the core package.

### **Package Boundaries**
- **[project]-core**: Only interface models - no business logic or external dependencies
- **[project]-api**: Complete implementation - business logic, services, database integration, provider pattern
- **[project]-tui**: Consumes [project]-core models and calls [project]-api endpoints

## Common Tasks and Commands

### **Development Workflow**
```bash
# Install dependencies
uv sync

# Start development server
make dev                   # Correctly references [project]_api.main:app

# Code quality (run after making changes)
make format                # Format code with ruff
make lint                  # Run linting checks
make check                 # Combined format-check + lint
make fix                   # Auto-fix all issues + format

# Run tests
make test-unit             # Unit tests only
make test-integration      # Integration tests (requires container)

# Container operations
make up                    # Start with docker-compose
make down                  # Stop containers
make logs                  # View container logs

# Workflow testing
make workflow              # Complete build→start→test→status
make quick-test           # Start, test, stop

# Analysis and reporting
make analysis             # View data analysis and insights
make analysis-detail CATEGORY=[category_name]
```

### **Manual Workflow Testing**
When asked to "run the workflow manually" against the API, execute these steps:
1. **Query for available work**: `GET /v1/[data-source]` to find items requiring processing
2. **Create a task**: `POST /v1/tasks` with the selected item identifier
3. **Poll for status**: `GET /v1/tasks/{id}` until status is "completed" or "failed"
4. **Obtain and verify results**: `GET /v1/tasks/{id}/results` to validate the output structure and content

### **Package Development**
```bash
# Work with individual packages
cd packages/[project]-core && uv sync    # Interface models only
cd packages/[project]-api && uv sync     # Complete implementation
cd packages/[project]-tui && uv sync     # Terminal interface

# Access database (SQLite task storage)
make db-shell

# Backup task database
make backup-db
```

## Key Configuration

### **Environment Variables**
- `[PROJECT]_API_KEY`: External service API key (if required)
- `[PROJECT]_DATABASE_URL`: Database connection for main data (readonly recommended)
- `[PROJECT]_SQLITE_DATABASE_URL`: SQLite path for task storage

### **Provider Pattern Configuration**
The provider pattern in `[project]_api/providers.py` manages:
- **Database Sessions**: Enhanced with built-in transaction management
- **Service Dependencies**: Task manager, analysis services, aggregation services
- **Task Queue**: Configuration and dependency injection
- **Transaction Handling**: Automatic commit/rollback for database operations

### **Transaction Management Usage**
```python
# Simple operations (no transaction needed)
async def read_data(session = Depends(get_db_session)):
    result = await session.execute(statement)
    return result.fetchall()

# Transactional operations (automatic commit/rollback)
async def write_data(session = Depends(get_db_session)):
    async with session:
        await session.execute(insert_statement)
        await session.execute(update_statement)
        # Commits automatically on success
        # Rolls back automatically on exceptions
```

### **Rate Limiting**
- **Core Service**: [X] requests/minute, [Y] concurrent
- **Aggregation Service**: [X] requests/minute, [Y] concurrent
- **Retry Logic**: Exponential backoff with [N] max retries

### **Classification Categories** ([N] total)
Define your project's classification system here:
```
Category Group 1: [list categories]
Category Group 2: [list categories]
Category Group 3: [list categories]
General: timeout_error, assertion_failure, diverse_issues, unknown_error
```

## Troubleshooting Common Issues

### **uv Workspace Issues**
- **Import errors**: Ensure using `uv sync` from workspace root, not individual packages
- **Module not found**: Use `make dev` which sets correct PYTHONPATH for [project]_api.main:app
- **Package dependencies**: Individual packages have minimal deps - [project]-api has full implementation

### **API Errors**
- **500 on task creation**: Check database connectivity and external service API keys
- **404 on data lookup**: Item ID may not exist or may not be the correct type
- **Rate limit errors**: Check external service quota and rate limiter configuration

### **Container Issues**
- **Container won't start**: Check environment variables in .env file
- **Database connection**: Verify connection string and network access
- **Data access failures**: Expected for missing data sources, categorized appropriately

### **Service Issues**
- **JSON parsing errors**: Enhanced parser handles malformed service responses
- **Category normalization**: Fuzzy matching maps service responses to standard categories
- **Fallback handling**: System tracks and reports when fallbacks are used

### **Provider Pattern Issues**
- **Dependency injection errors**: Ensure providers are properly configured in `providers.py`
- **Transaction issues**: Use `async with session:` for operations requiring ACID guarantees
- **Test failures**: Override dependencies using `app.dependency_overrides` for testing

## Code Quality Standards

### **Continuous Code Quality (CRITICAL)**
**As an AI coding assistant, you MUST run linting and formatting commands after making any code changes to maintain project standards:**

```bash
# After making any code changes, run these commands:
make format                # Format all code with ruff (auto-fixes whitespace, imports)
make lint                  # Check for linting issues 
make check                 # Combined: format-check + lint (for CI validation)

# If linting issues exist:
make lint-fix              # Auto-fix issues where possible
make fix                   # Combined: lint-fix + format (fix everything possible)
```

**Integration into Development Workflow:**
1. **After editing any .py file** → Run `make format` immediately
2. **Before committing changes** → Run `make check` to validate code quality
3. **If linting errors remain** → Run `make fix` to auto-resolve, then address remaining issues manually
4. **Include in every code change workflow** → This prevents accumulation of style issues

**Ruff Configuration:**
- **Centralized**: All rules defined in workspace root `pyproject.toml`
- **Workspace-wide**: Applies consistently across all packages ([project]-core, [project]-api, [project]-tui)
- **Import sorting**: Replaces isort, configured for [project] packages as first-party
- **Line length**: 100 characters maximum
- **Target**: Python 3.12 with modern practices

### **When Adding Features**
1. **Determine package location**: Interface models in [project]-core, implementation in [project]-api
2. **Use provider pattern**: Add dependencies through `providers.py` for testability
3. **Start with tests** to understand interfaces and edge cases
4. **Extract pure functions** for business logic when possible  
5. **Use proper async patterns** for all I/O operations
6. **Follow existing patterns** for error handling and logging
7. **Add transaction support** where database operations are involved
8. **Run `make format && make lint`** after implementing changes
9. **Update documentation** including API specs and README

### **When Fixing Bugs**
1. **Write a failing test** that reproduces the issue
2. **Fix the minimal code** required to make test pass
3. **Run `make fix`** to ensure code style compliance
4. **Consider refactoring** if the fix reveals design issues
5. **Verify integration** with end-to-end tests

### **Performance Considerations**
- **Rate limiting** is conservative - adjust based on external service quotas
- **Concurrent processing** within tasks ([N] units default)
- **Database queries** should be efficient and properly indexed
- **Transaction overhead** - use transactions only when needed for ACID guarantees
- **Data extraction** optimized for real-world data formats

### **Package Architecture**
- **[project]-core**: Minimal interface models only - no business logic, external dependencies, or utilities
- **[project]-api**: Complete implementation with all business logic, services, infrastructure, and provider pattern
- **[project]-tui**: Consumer of [project]-core models and [project]-api endpoints
- **Clear separation**: Interface definitions vs. implementation details

## Customization Guide

### **Adapting This Framework**
1. **Replace placeholders**: Search and replace `[PROJECT_NAME]`, `[project]`, `[PROJECT]` with your project details
2. **Define your domain**: Update the Core Mission section with your specific inputs, processes, and outputs
3. **Customize services**: Replace AI services with your domain-specific business logic services
4. **Update categories**: Define your project's classification or categorization system
5. **Adjust rate limits**: Configure rate limiting based on your external service requirements
6. **Add domain endpoints**: Extend the v1 API with your project-specific endpoints

### **Framework Benefits**
- **Proven Architecture**: Battle-tested patterns for scalable Python services
- **Modern Toolchain**: uv workspace, FastAPI, async/await, Pydantic
- **Clean Code**: Provider pattern, dependency injection, transaction management
- **Testability**: Clear boundaries, dependency overrides, unit and integration tests
- **Maintainability**: Code quality automation, structured logging, error handling
- **Deployability**: Container-ready with docker-compose

This framework should guide development decisions and help maintain consistency across any Python project using these architectural patterns.

---

*Framework template derived from production codebase. Customize placeholders and domain-specific sections for your project.*
