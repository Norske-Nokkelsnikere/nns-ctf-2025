FROM rust:1.86-slim

WORKDIR app/
COPY . ./
RUN cargo build --release
CMD ["cargo", "run", "--release"]