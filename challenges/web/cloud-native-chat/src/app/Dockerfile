FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS app
WORKDIR /app
COPY . ./
RUN uv sync --locked
CMD ["uv", "run", "fastapi", "run"]
