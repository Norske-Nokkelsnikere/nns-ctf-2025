from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

flag = b"NNS{???????????????????????????????????????????????}"
key = os.urandom(16)

def encrypt(pt):
	iv = os.urandom(16)
	ct = AES.new(iv, AES.MODE_CFB, key, segment_size=128).encrypt(pad(pt, 16))
	return iv.hex(), ct.hex()

iv0, ct0 = encrypt(b"One documentation a day keeps the bugs away or whatever my doctor used to say")
iv1, ct1 = encrypt(flag)

print(f"{iv0 = }")
print(f"{ct0 = }")
print(f"{iv1 = }")
print(f"{ct1 = }")
