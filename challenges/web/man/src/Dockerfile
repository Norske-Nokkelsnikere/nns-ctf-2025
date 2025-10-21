FROM oven/bun:1.2.20-debian

RUN apt-get update && apt-get install -y man dumb-init

WORKDIR /app
COPY ./package.json /app/package.json
COPY ./bun.lock /app/bun.lock
COPY ./src /app/src

RUN bun install

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD [ "bun", "run", "/app/src/index.ts" ]
