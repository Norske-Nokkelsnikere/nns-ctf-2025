FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/

WORKDIR /app
COPY . ./
RUN uv sync --locked

ENTRYPOINT ["socat", "TCP-LISTEN:1337,fork,reuseaddr", "EXEC:uv run point_encryption2.py"]
