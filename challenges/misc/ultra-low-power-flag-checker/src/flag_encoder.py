from Crypto.Util.number import getPrime

p = getPrime(1024)
q = getPrime(1024)

n = p * q
phi = (p - 1) * (q - 1)

e = 65537

d = pow(e, -1, phi)

flag = b"NNS{r3memb3r_t0_h1de_y0ur_p0w3r_u54ag3}"

m = int.from_bytes(flag, byteorder="little")

c = pow(m, e, n)

print("n =", n)
print("e =", e)
print("d =", d)
print("c =", c)