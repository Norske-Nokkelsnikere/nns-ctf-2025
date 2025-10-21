from Crypto.Util.number import *
from pwn import xor 

ct = bytes.fromhex(f"42548d6593f5b924fabfa291c19cf0db72d77f72f5484af6")

def fib(n):
    M = matrix(ZZ, [[1, 1],
                    [1, 0]])
    return (M^n)[0, 1]

A = 31333337
B = 3133333337
C = 313333333337
D = 31333333333337

k = 1337 * pow(fib(A) % C,B,D**4)
key = long_to_bytes(k)
pt = xor(key,ct)
print(pt)
# NNS{Fl4g0n4cc1_s3qu3nc3}