# syntax=docker/dockerfile:1

# Stage 1: Install Python dependencies
FROM python:3.14-slim AS builder

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY src/ src/

# Install deps, then strip __pycache__ to shrink the runtime
# image.
RUN touch README.md \
    && uv sync --locked --no-dev \
    && find /app/.venv -type d -name __pycache__ \
        -exec rm -rf {} +

# Stage 2: Runtime (no uv, no build tools)
FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8002

ENTRYPOINT ["notifier"]
