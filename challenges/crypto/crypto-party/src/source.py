from Crypto.Util.number import bytes_to_long
from secrets import randbits
from hashlib import sha384
from ecdsa import curves
import os

secret_key = bytes_to_long(os.getenv("FLAG", "NNS{fake_flag}").encode())
MAX_INVITES = 15

curve_obj = curves.NIST384p
G = curve_obj.generator
n = curve_obj.order

def invite(m):
    h = bytes_to_long(sha384(m.encode()).digest())
    k = randbits(h.bit_length())
    P = k * G
    r = P.x() % n
    s = (pow(k, -1, n) * (h + r * secret_key)) % n
    return r, s

try:
    print(f"Wassup")
    print(f"The guest list is a bit crammed, but you can invite up to {MAX_INVITES} friends.")
    for _ in range(MAX_INVITES):
        m = input("Enter the name of your friend: ").strip()
        r, s = invite(m)
        print(f"Alright, here is {m}'s invite code:")
        print(f"Invitation code = {r}:{s}")
except Exception as e:
    pass
