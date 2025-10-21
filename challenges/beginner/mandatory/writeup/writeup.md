gdb ./chal

disas main

where the `d4` is loadeds
```
0x00005555555551fb <+50>:    lea    0x2e0e(%rip),%rdx        # 0x555555558010 <d4>
```

break *main
run

x/25bx 0x555555558010

then use python script do xor it with `0x37`