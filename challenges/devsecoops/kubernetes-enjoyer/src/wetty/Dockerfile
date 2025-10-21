FROM wettyoss/wetty
RUN apk add socat
CMD ["--base", "/", "--command", "socat STDIO,raw,echo=0 TCP-CONNECT:challenge:1337"]