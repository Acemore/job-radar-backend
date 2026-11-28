FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PATH="/venv/bin:${PATH}"

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache

COPY src/ ./src
COPY scripts/ ./scripts
COPY alembic/ ./alembic
COPY alembic.ini ./

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
