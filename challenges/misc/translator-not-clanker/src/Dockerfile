FROM debian:trixie-slim

COPY ./encode.py /encode.py

RUN apt-get update \
    && apt-get install -y --no-install-recommends socat python3 \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 3452

ENTRYPOINT [ "/usr/bin/socat" ]
CMD [ "-T600", "TCP-LISTEN:3452,reuseaddr,fork", "EXEC:'timeout 600 python3 /encode.py',pty,stderr,setsid,rawer,echo=0" ]
