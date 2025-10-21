flag = b"NNS{w0w_1_l0v3_r3v3rs1ng}"
key = 0x37
encoded = [hex(c ^ key) for c in flag]
print(", ".join(encoded))