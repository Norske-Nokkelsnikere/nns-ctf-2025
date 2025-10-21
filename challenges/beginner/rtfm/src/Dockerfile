FROM oven/bun:1.2.20-debian

RUN apt-get update && apt-get install -y openssl dumb-init

WORKDIR /app
COPY ./package.json /app/package.json
COPY ./bun.lock /app/bun.lock
COPY ./src /app/src
COPY ./prisma /app/prisma
COPY ./.env /app/.env

RUN bun i
RUN bunx prisma generate
RUN bunx prisma db push

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD [ "bun", "run", "/app/src/index.ts" ]
