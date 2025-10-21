from Crypto.Util.number import getPrime, bytes_to_long, GCD # pip install pycryptodome

m = bytes_to_long(b"NNS{??????????????????????}")
e1 = 0x10001
e2 = getPrime(15)

while True:
    p = getPrime(512)
    q = getPrime(512)
    n = p * q
    phi = (p-1)*(q-1)
    if GCD(e1, phi) == 1 and GCD(e2, phi) == 1:
        break

c1 = pow(m, e1, n)
c2 = pow(m, e2, n)

print(f"n  = 0x{n:x}")
print(f"c1 = 0x{c1:x}")
print(f"c2 = 0x{c2:x}")
