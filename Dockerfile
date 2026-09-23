FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/venv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache

COPY src/ ./src
COPY scripts/ ./scripts

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
