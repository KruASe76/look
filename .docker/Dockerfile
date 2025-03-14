FROM ghcr.io/astral-sh/uv:bookworm-slim

WORKDIR /app
COPY app/ ./app/
COPY certs/ ./certs/
COPY main.py pyproject.toml uv.lock ./

ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --compile-bytecode

CMD uv run python3 main.py
