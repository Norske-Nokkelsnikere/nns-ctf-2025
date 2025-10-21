FROM pwntools/pwntools@sha256:1707bef16a3fb924d53231d899eeecaf18b5ebbb78e23c38d41dcd19d147bf6b

ENV TERM=xterm
ENV PWNLIB_NOTERM=1

USER root
WORKDIR /opt

RUN apt-get update --fix-missing && \
    apt-get install -y socat

RUN echo never > /root/.cache/.pwntools-cache-3.12/update
COPY chall.py .
COPY flag.txt .
EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:python3 chall.py,pty,raw,echo=0,stderr,setsid,sigint"]