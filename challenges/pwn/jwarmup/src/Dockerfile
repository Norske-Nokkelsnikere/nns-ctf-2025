FROM azul/zulu-openjdk-debian:21.0.8-21.44 AS builder
WORKDIR /usr/share/app
COPY Main.java .
RUN javac Main.java && rm Main.java

FROM azul/zulu-openjdk-debian:21.0.8-21.44-jre-headless

RUN apt-get update && apt-get install -y socat
RUN useradd -m -u 1001 -s /bin/bash app
USER app

WORKDIR /usr/share/app
COPY --from=builder /usr/share/app/Main.class .

ENTRYPOINT ["socat", "TCP-LISTEN:1337,fork,reuseaddr", "EXEC:'java -Xmx8G -XX:+UnlockExperimentalVMOptions -XX:-CreateCoredumpOnCrash Main',stderr"]
