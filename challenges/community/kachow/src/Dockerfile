FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y socat gcc && useradd -m ctf

WORKDIR /home/ctf
USER ctf

COPY ./kachow.c .
RUN gcc -o ./kachow ./kachow.c && chmod 555 kachow

ENTRYPOINT ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:/home/ctf/kachow,stderr"]
