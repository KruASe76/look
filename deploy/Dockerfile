FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
COPY app/ ./app/
COPY main.py pyproject.toml uv.lock ./

ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/cache/uv
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    uv sync --frozen --no-dev --compile-bytecode

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
CMD ["uv", "run", "--no-dev", "main.py"]
EXPOSE $APP_PORT
