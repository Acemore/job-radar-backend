# JobRadar

[![ci](https://github.com/Acemore/job-radar-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/Acemore/job-radar-backend/actions/workflows/ci.yml)

An asynchronous ETL system engineered for streaming processing, unification, and analytics of vacancy data collected from external platforms.

For a detailed structural overview of data streams and components, see the [Architectural Data Flow Diagram](docs/architecture.md).

## Engineering Highlights

* **Resilient Routing Layer:** Built with httpx. Uses a round-robin routing strategy across independent gateways with configuration parameters isolated within concurrent frames to guarantee network stability under heavy load.
* **Database Idempotency:** Implements atomic batch inserts managed by the PostgreSQL core via `INSERT ... ON CONFLICT (link) DO NOTHING` syntax, eliminating redundant lookup overhead.
* **Non-Blocking File I/O:** Generation of CSV and Excel reports is offloaded using `asyncio.to_thread` to ensure the main asynchronous Event Loop never encounters file system performance bottlenecks.
* **Architecture Decision Records (ADR):** The project tracks key architectural updates using formal ADRs.

## Tech Stack

* **Core Backend:** Python (Async / Await), FastAPI (Lifespan, Uvicorn), Asyncio, HTTPX, Selectolax.
* **Persistence & Migrations:** PostgreSQL, SQLAlchemy 2.0 (Mapped / Async), Alembic.
* **Quality & Infrastructure:** Pytest (Asyncio / Mocking), Structlog (JSON logging), Pydantic-settings, uv, Docker, Docker Compose, Pre-commit hooks (Ruff, Mypy).

## Local Development

### 1. Environment Configuration

Duplicate the provided infrastructure configuration template and adjust your local parameters:

```bash
cp .env.sample .env
```

### 2. Standard Local Execution (CLI Engine)

To run the automated data collection, console analytics, and report generation via host machine:

```bash
# Spin up isolated PostgreSQL container
docker compose up -d postgres

# Sync dependencies using uv manager
uv sync

# Run database migrations via Alembic
uv run alembic upgrade head

# Execute ETL pipeline and compile reports
PYTHONPATH=. uv run python scripts/cli.py
```

*Note: Successful execution prints market analytics to the console and compiles vacancies_report.csv and vacancies_report.xlsx targets in the root directory.*

### 3. Full Multi-Container Deployment (API & Infrastructure)

To orchestrate and deploy the entire application stack including the live web API service:

```bash
# Build multi-stage images and run full application layer stack dynamically
docker compose up -d --build
```

### 4. Automated Tests

Run the comprehensive test suite locally:

```bash
uv run pytest
```
