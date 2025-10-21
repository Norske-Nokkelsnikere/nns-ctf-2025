# Stage 1: Build frontend with Bun
FROM oven/bun:1.2.20-alpine AS web-build

WORKDIR /app
COPY ./web ./web
WORKDIR /app/web

RUN bun install
RUN bun run build

# Stage 2: Build application with Rust
FROM rust:1.88.0-slim-bookworm AS rust-build

WORKDIR /app
COPY .sqlx ./.sqlx
COPY migrations ./migrations
COPY src ./src
COPY Cargo.lock ./Cargo.lock
COPY Cargo.toml ./Cargo.toml
COPY --from=web-build /app/web/dist ./web/dist
RUN ls

# RUN apt-get update && apt-get install -y pkg-config libssl-dev

RUN cargo install sqlx-cli --no-default-features --features sqlite,rustls
ENV DATABASE_URL=sqlite:db/linktea.db
RUN mkdir db
RUN cargo sqlx database setup

RUN cargo build --release

# Stage 3: Run binary :-)
FROM debian:12.11-slim

WORKDIR /app
COPY --from=rust-build /app/target/release/linktea ./
RUN adduser --disabled-password --shell "/sbin/nologin" --uid 1001 linktea
# RUN apk add chromium=131.0.6778.108-r0
RUN mkdir db
RUN chown linktea:linktea ./db

RUN apt-get update && apt-get install -y curl unzip
# Thanks stackoverflow!
RUN apt-get install -y unzip xvfb libxi6 libgconf-2-4 jq libjq1 libonig5 libxkbcommon0 libxss1 libglib2.0-0 libnss3 \
libfontconfig1 libatk-bridge2.0-0 libatspi2.0-0 libgtk-3-0 libpango-1.0-0 libgdk-pixbuf2.0-0 libxcomposite1 \
libxcursor1 libxdamage1 libxtst6 libappindicator3-1 libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libxfixes3 \
libdbus-1-3 libexpat1 libgcc1 libnspr4 libgbm1 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxext6 \
libxrandr2 libxrender1 gconf-service ca-certificates fonts-liberation libappindicator1 lsb-release xdg-utils

RUN mkdir /chromium
RUN curl https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1440669%2Fchrome-linux.zip?alt=media -o /chromium/dl.zip
RUN unzip /chromium/dl.zip -d /chromium/
ENV CHROME="/chromium/chrome-linux/chrome"

USER linktea:linktea
CMD ["/app/linktea"]
