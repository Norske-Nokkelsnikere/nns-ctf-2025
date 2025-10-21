from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pwn import xor

iv0 = bytes.fromhex('4858c64be12fbb05c648d6ef4be134a1')
ct0 = bytes.fromhex('f865533a29fa083996223e60d0b4a62be1e7cfac3ef1981ed53564b9eb2e2b36d28bfcaf6d656deb365e26c6d89782f9abd82b99f75a7b72c564b48a2598577492c459e089c798bf02c7fb621930ef84')
iv1 = bytes.fromhex('ef73d8fa5ce9521495abcea79f6a2d4b')
ct1 = bytes.fromhex('bd669aa9cb3ae0a46b46633eccd38a81c9e6c102f34d0809c3aa7cf6b824615cf9534275b23b97ce5a9efe039985dbcf5e3edc8266ff58c3629f40fe277e460c')

pt0 = b"One documentation a day keeps the bugs away or whatever my doctor used to say"
pt_xor_ct = xor(ct0, pt0)

IV = AES.new(iv0, AES.MODE_ECB).decrypt(pt_xor_ct[:16])

flag = AES.new(iv1, AES.MODE_CFB, IV, segment_size=128).decrypt(ct1) 
print(unpad(flag, 16).decode()) 
