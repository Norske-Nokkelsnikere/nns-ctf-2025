FROM python:3.13-alpine AS base
FROM base AS builder

# Use uv
COPY --from=ghcr.io/astral-sh/uv:0.8.13 /uv /bin/uv

# UV_COMPILE_BYTECODE=1 compiles Python bytecode for faster startup
# UV_LINK_MODE=copy ensures dependencies are copied (isolated env)
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app
COPY pyproject.toml requirements.txt /app/
RUN uv venv
RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install -r requirements.txt --no-deps

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install -e .

# minimal and optimized
FROM base

COPY --from=builder /app /app
RUN chmod 755 /app/src/parcellocker

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/my_parcel || exit 1
# guest user
USER 405
EXPOSE 8000
CMD	["/app/.venv/bin/fastapi","run","/app/src/parcellocker/main.py","--port","8000","--root-path","/api"]
