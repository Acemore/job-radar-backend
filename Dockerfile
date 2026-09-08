FROM python:3.14-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
