def rc4(key: bytes, data: bytes) -> bytes:
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]

    i = j = 0
    result = []
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        result.append(byte ^ K)

    return bytes(result)


key = b"dolphin"
flag = bytes.fromhex("f55f66d8a1b2c37980ba05fd7b7cf13fef144ff8a508b325871f3b192c5cafcddf1274a94e6c199011de305d10e175ba1af5020723971e3f9e64e4dabb6abc0430ac29993785c6fecf43c1c2bda2412a2741f7b60573700fea666525a5497989")

flag = rc4(key, flag)

print(flag.decode())