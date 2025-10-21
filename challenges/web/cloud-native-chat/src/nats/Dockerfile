FROM nats:2.11.6 AS nats
COPY nats.conf /etc/nats/custom.conf
CMD ["-js", "-c", "/etc/nats/custom.conf"]
