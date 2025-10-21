FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN apt-get update && \
    apt-get install -y curl bash git && \
    rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos "" ctf

RUN curl -L https://foundry.paradigm.xyz | bash && \
    . /root/.bashrc && \
    foundryup && \
    chmod 755 -R /root

ENV PATH="/root/.foundry/bin:${PATH}"

RUN mkdir /var/log/ctf && chown ctf:ctf /var/log/ctf

USER ctf
WORKDIR /home/ctf
COPY . ./

RUN uv sync --locked

RUN forge install foundry-rs/forge-std --no-git \
    && forge clean \
    && forge build

EXPOSE 8000
ENTRYPOINT ["uv", "run", "fastapi", "run"]
