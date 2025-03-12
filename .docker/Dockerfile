FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app
COPY .. .

ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --compile-bytecode

CMD uv run fastapi run main.py --port 8000
