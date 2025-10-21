from string import ascii_lowercase, ascii_uppercase, digits

from pwn import remote

BASE64 = ascii_uppercase + ascii_lowercase + digits + "+/"


def b64d(encoded: str) -> str:
    result = ""
    for e in encoded.replace("=", ""):
        n = BASE64.index(e)
        result += f"{n:06b}"

    return result


with remote("your instance url", 3452) as io:
    # Just a high enough number
    payload = "a " * 100
    io.sendlineafter(b"< ", payload.encode("utf-8"))

    io.recvuntil(b"> ")
    output = io.recvline().decode("utf-8").split()


flag_bits = "".join([b64d(o)[-4:] for o in output])
flag = int.to_bytes(int(flag_bits, 2), len(flag_bits) // 8)
print(flag.decode("utf-8", errors="ignore"))
