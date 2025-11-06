FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /bot

ENV UV_NO_DEV=true
ENV UV_LOCKED=true
ENV UV_COMPILE_BYTECODE=true
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/cache/uv

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    uv sync --group bot --no-install-project

COPY bot/ ./bot/
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    uv sync --group bot

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
ENTRYPOINT ["uv", "run", "-m", "bot.cli"]
EXPOSE $APP_PORT
