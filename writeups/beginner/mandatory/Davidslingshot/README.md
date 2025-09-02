# **mandatory-rev**

### Step 1 – Initial Analysis

I was given an **ELF executable** named `mandatory`.

To understand how it works, I loaded it into **Ghidra** for static analysis.

---

### Step 2 – Decompiled Code

Looking at the decompiled code, I found an interesting snippet:

```c
local_10 = *(long *)(in_FS_OFFSET + 0x28);
for (local_dc = 0; local_dc < 0x19; local_dc = local_dc + 1) {
    local_d8[(int)local_dc] = d4[(int)local_dc] ^ 0x37; // XOR decryption
}
local_bf = 0;
printf("enter flag: ");
__isoc99_scanf("%127s",local_98);
iVar1 = strcmp(local_98,(char *)local_d8);
if (iVar1 == 0) {
    puts("correct!");
}
else {
    puts("wrong flag, try again.");
}
```

From this, it was clear:

* The **flag is stored in `d4`**.
* Each byte is **XORed with `0x37`** to decrypt it.
* The decrypted string is then compared against user input.

So the task was: **dump the bytes at `d4` and XOR them with `0x37`.**

---

### Step 3 – Finding `d4`

Using gdb, I located `d4` at memory address `0x4010`:

```bash
$ gdb -q ./mandatory
Reading symbols from ./mandatory...
(No debugging symbols found in ./mandatory)
(gdb) info variables d4
All variables matching regular expression "d4":

Non-debugging symbols:
0x00000000004010  d4
(gdb) p &d4
$1 = (<data variable, no debug info> *) 0x4010 <d4>
```

---

### Step 4 – Inspecting Memory

Next, I dumped 25 bytes from that address:

```bash
(gdb) x/25bx 0x4010
0x4010 <d4>:   0x79 0x79 0x64 0x4c 0x40 0x07 0x68 0x45
0x4018 <d4+8>: 0x06 0x68 0x5b 0x07 0x41 0x04 0x68 0x45
0x4020 <d4+16>:0x41 0x04 0x45 0x44 0x06 0x59 0x50 0x4a
```

Clearly, these bytes didn’t look like plain ASCII → they needed to be XORed with `0x37`.

---

### Step 5 – Extracting the Flag

Instead of writing an external script, I decrypted directly inside gdb with:

```bash
printf "%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c\n", \
((unsigned char*)0x4010)[0]^0x37, ((unsigned char*)0x4010)[1]^0x37, \
((unsigned char*)0x4010)[2]^0x37, ((unsigned char*)0x4010)[3]^0x37, \
((unsigned char*)0x4010)[4]^0x37, ((unsigned char*)0x4010)[5]^0x37, \
((unsigned char*)0x4010)[6]^0x37, ((unsigned char*)0x4010)[7]^0x37, \
((unsigned char*)0x4010)[8]^0x37, ((unsigned char*)0x4010)[9]^0x37, \
((unsigned char*)0x4010)[10]^0x37, ((unsigned char*)0x4010)[11]^0x37, \
((unsigned char*)0x4010)[12]^0x37, ((unsigned char*)0x4010)[13]^0x37, \
((unsigned char*)0x4010)[14]^0x37, ((unsigned char*)0x4010)[15]^0x37, \
((unsigned char*)0x4010)[16]^0x37, ((unsigned char*)0x4010)[17]^0x37, \
((unsigned char*)0x4010)[18]^0x37, ((unsigned char*)0x4010)[19]^0x37, \
((unsigned char*)0x4010)[20]^0x37, ((unsigned char*)0x4010)[21]^0x37, \
((unsigned char*)0x4010)[22]^0x37, ((unsigned char*)0x4010)[23]^0x37, \
((unsigned char*)0x4010)[24]^0x37
```

---

### Step 6 – Flag

The decrypted output gave the correct **flag** 🎉.

---

