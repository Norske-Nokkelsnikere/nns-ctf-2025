FROM azul/zulu-openjdk-debian:11-latest AS builder

RUN useradd -m -u 1001 -s /bin/bash builder
USER builder

WORKDIR /usr/src/app
COPY --chown=builder:builder . .
RUN ./gradlew --no-daemon shadowJar

FROM azul/zulu-openjdk-debian:11-jre-latest

RUN apt-get update && apt-get install -y socat
RUN useradd -m -u 1001 -s /bin/bash app
USER app

WORKDIR /usr/share/app
COPY --from=builder "/usr/src/app/build/libs/grooves-1.0-SNAPSHOT-all.jar" app.jar
COPY --chown=app:app flag.txt .

ENTRYPOINT ["socat", "TCP-LISTEN:1337,fork,reuseaddr", "EXEC:java -jar app.jar"]
