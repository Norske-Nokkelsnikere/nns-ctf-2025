FROM debian:13-slim AS build

RUN apt-get update && apt-get install -y elan git socat && useradd -m -u 1001 -s /bin/bash ctf

USER ctf
WORKDIR /home/ctf/challenge
COPY . .

RUN lake build collatz
RUN cp /home/ctf/challenge/.lake/build/bin/collatz ./collatz

ENTRYPOINT ["socat", "TCP-LISTEN:1337,fork,reuseaddr", "EXEC:/home/ctf/challenge/collatz,stderr,pty,echo=0"]
