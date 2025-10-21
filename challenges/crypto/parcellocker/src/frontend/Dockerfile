
FROM	node:22-alpine	AS	builder
WORKDIR	/app
COPY	package*.json	./
RUN	npm ci
COPY	.	.
RUN	npm run build
RUN	npm prune --omit=dev
FROM	node:22-alpine
ENV	NODE_ENV	production
WORKDIR	/app
COPY	package.json	./
COPY	--from=builder /app/build	./build
EXPOSE	3000
CMD	["node","build/index.js"]
