from hashlib import sha384
from Crypto.Util.number import long_to_bytes, bytes_to_long
from pwn import process, remote

p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff
a = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000fffffffc
b = 0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef
E = EllipticCurve(GF(p), (a, b))
G = E(0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7, 0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f)

TARGET = 384 - 26
MAX_SIGNS = 15

# Bruteforced messages in c++, 26 leading 0s in sha384(m)
m_list = ["5831510802864336587", "4043571505136580158", "12526062053017315165", "10041337858200554269", "1637419369778128749", "14809818597197070392", "1110442837066371244", "3411418725862600623", "4880688063777367720", "12379504707119173067", "2006773378711163144", "7933584175731495031", "16545122915669964690", "5008991014443739040", "6449892206914444070"]
h_list = []
r_list = []
s_list = []

io = process(["python3", "source.py"])
io.recvuntil(b"friends.\n")
for m in m_list:
    io.sendline(m.encode())
    io.recvline()
    r,s = io.recvline().split(b"=")[1].split(b":")
    r_list.append(int(r.strip()))
    s_list.append(int(s.strip()))
    h_list.append(bytes_to_long(sha384(m.encode()).digest()))
io.close()

def shortest_vectors(B):
    B = B.LLL()
    for row in B.rows():
        if not row.is_zero():
            yield row

class PartialInteger:
    def __init__(self, value, mask, bits):
        self.v = int(value)
        self.m = int(mask)
        self.bit_length = bits

    def get_known_msb(self):
        msb_val = 0
        msb_len = 0
        for i in reversed(range(self.bit_length)):
            if (self.m >> i) & 1:       
                msb_val = (msb_val << 1) | ((self.v >> i) & 1)
                msb_len += 1
            else:                                
                break
        return msb_val, msb_len

    def get_unknown_lsb(self):
        lsb_len = 0
        for i in range(self.bit_length):
            if (self.m >> i) & 1:        
                break
            lsb_len += 1
        return lsb_len

    def sub(self, parts):
        low = int(parts[0])
        lsb_len  = int(self.get_unknown_lsb())
        mask_lsb = int((1 << lsb_len) - 1)      
        return Integer((int(self.v) & ~mask_lsb) | (low & mask_lsb))

    def __repr__(self):
        bits = ''.join(reversed(self.to_bits_le()))
        return f"<PartialInteger {bits}>"

    def to_bits_le(self):
        return [
            str((self.v >> i) & 1) if ((self.m >> i) & 1) else '?'
            for i in range(self.bit_length)
        ]

def attack(a, b, m, X):
    n1 = len(a)
    n2 = len(a[0])
    B = matrix(QQ, n1 + n2 + 1, n1 + n2 + 1)
    for i in range(n1):
        for j in range(n2):
            B[n1 + j, i] = a[i][j]

        B[i, i] = m
        B[n1 + n2, i] = b[i] - X // 2

    for j in range(n2):
        B[n1 + j, n1 + j] = X / QQ(m)

    B[n1 + n2, n1 + n2] = X

    for v in shortest_vectors(B):
        xs = [int(v[i] + X // 2) for i in range(n1)]
        ys = [(int(v[n1 + j] * m) // X) % m for j in range(n2)]
        if all(y != 0 for y in ys) and v[n1 + n2] == X:
            yield xs, ys


def dsa_known_msb(n, h, r, s, k):
    a = []
    b = []
    X = 0
    for hi, ri, si, ki in zip(h, r, s, k):
        msb, msb_bit_length = ki.get_known_msb()
        shift = 2 ** ki.get_unknown_lsb()
        a.append([(pow(si, -1, n) * ri) % n])
        b.append((pow(si, -1, n) * hi - shift * msb) % n)
        X = max(X, shift)
    for k_, x in attack(a, b, n, X):
        yield x[0], [ki.sub([ki_]) for ki, ki_ in zip(k, k_)]


TOTAL_BITS = 384
KNOWN_BITS = TOTAL_BITS - TARGET
MASK_TOP = ((1 << KNOWN_BITS) - 1) << (TOTAL_BITS - KNOWN_BITS) 
KNOWN_VALUE = 0  # all top bits are 0

k_partial = [PartialInteger(KNOWN_VALUE, MASK_TOP, TOTAL_BITS) for _ in range(len(r_list))]
print(long_to_bytes(next(dsa_known_msb(E.order(), h_list, r_list, s_list, k_partial))[0]))