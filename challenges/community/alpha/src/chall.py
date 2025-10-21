from capstone import *
from pwn import *

context.update(arch="amd64", os="linux")
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.skipdata = True

def die(msg: str): sys.exit(warn(msg))

try:
    shellcode = bytes.fromhex(input(">> "))
    if not shellcode: die("Empty input")
except Exception: die("Invalid hex")

sorted_shellcode = b"".join(bytes(i.bytes) for i in sorted(list(md.disasm(shellcode, 0)), key=lambda i: i.mnemonic or ""))

info("Here is your shellcode before, ugly and unaesthetic ಠ_ಠ")
print(disasm(shellcode))

info("Here it is after, literally perfect (●'◡'●)")
print(disasm(sorted_shellcode))

info("As a special prize, I'll even run it!")
with process(make_elf(sorted_shellcode, extract=False), stdin=0) as p:
    p.interactive()
