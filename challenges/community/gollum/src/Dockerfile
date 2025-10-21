FROM golang:1.25rc2-bookworm

RUN go install github.com/codeskyblue/gohttpserver@latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nginx libnginx-mod-http-modsecurity && \
    rm -rf /var/lib/apt/lists/*

WORKDIR "/usr/local/bin/"

COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/file_checker.sh config/docker-entrypoint.sh ./
RUN chmod +x file_checker.sh docker-entrypoint.sh
COPY files/* /app/public/

EXPOSE 80

ENTRYPOINT ["./docker-entrypoint.sh"]
