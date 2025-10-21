from pwn import *

elf = ELF("./mandatory", checksec=False)

d4_data = elf.read(elf.symbols['d4'], 25)

flag = bytes([b ^ 0x37 for b in d4_data])

print(flag.decode())