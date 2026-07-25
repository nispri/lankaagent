# LankaAgent MCP Server — Dockerfile (FastMCP Tourism Data)

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Dependencies
FROM base AS deps

COPY pyproject.toml poetry.lock* ./
RUN poetry install --only=main --no-interaction --no-ansi

# Development
FROM deps AS development

RUN poetry install --with=dev --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD ["python", "-m", "mcp_server.main", "--transport", "streamable-http", "--port", "8000"]

# Build
FROM deps AS build

COPY . .
RUN python -m compileall -q mcp_server/

# Production
FROM python:3.12-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /app /app

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "mcp_server.main", "--transport", "streamable-http", "--port", "8000"]