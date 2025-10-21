FROM ubuntu@sha256:a08e551cb33850e4740772b38217fc1796a66da2506d312abe51acda354ff061

RUN apt-get update && apt-get install -y socat gcc && useradd -m ctf

WORKDIR /home/ctf
USER ctf

RUN echo "NNS{fake_flag}" > /home/ctf/flag.txt

COPY ./notes.c .
RUN gcc -o ./notes ./notes.c && chmod 555 notes

ENTRYPOINT ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:/home/ctf/notes,stderr"]
