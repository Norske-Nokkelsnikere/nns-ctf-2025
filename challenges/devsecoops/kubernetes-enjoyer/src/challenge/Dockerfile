FROM alpine:3.22.1
RUN apk add kubectl sudo socat && \
    adduser -D -H ctf && \
    echo "ctf ALL=(ALL) NOPASSWD: /usr/bin/kubectl" > /etc/sudoers.d/kubectl && \
    mkdir -m 000 -p /root/secretdirectorydonttouch/ && \
    mkdir -p /usr/local/sbin && \
    (chmod -R o-w / || true)

USER ctf
ENTRYPOINT ["socat", "TCP-LISTEN:1337,fork,reuseaddr", "EXEC:ash,pty,stderr,setsid,sigint,sane"]
