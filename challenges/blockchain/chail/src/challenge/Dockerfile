FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y curl bash git socat && \
    rm -rf /var/lib/apt/lists/*

RUN curl -L https://foundry.paradigm.xyz | bash && \
    . /root/.bashrc && \
    foundryup && \
    chmod 755 -R /root

ENV PATH="/root/.foundry/bin:${PATH}"
    
RUN rm -rf /root/.foundry/bin/chisel
COPY chisel /root/.foundry/bin/chisel
RUN chmod 777 /root/.foundry/bin/chisel

USER root
WORKDIR /root

RUN forge init --force .

EXPOSE 1337

CMD socat TCP-LISTEN:1337,reuseaddr,fork EXEC:"chisel",pty,stderr,setsid,sigint,sane