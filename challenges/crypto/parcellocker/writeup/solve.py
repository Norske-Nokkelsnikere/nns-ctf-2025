from Crypto.Util.number import bytes_to_long
from Crypto.PublicKey import RSA
import requests

# factored with cado-nfs docker image
privkey = RSA.import_key(
    """-----BEGIN RSA PRIVATE KEY-----
MIGpAgEAAiEAiDTUP+IEDd2Zulxi6efNXPgbdyk78KOHemPSyQdaUoUCAwEAAQIgSLWy7FtSALjg
PJze7LCibof+s2xC9cPKFcmGPBpJKwECEQCXckoaM9EbmpTEiLYzzWjBAhEA5j0aGXxLW1lHRM1M
sjA2xQIQMzueL5/8QmePzZcdDEZsugIQX5KWYUQKCkKZhd9OrplyzgIQGILhipzbZF+Ip0gqPQFl
aA==
-----END RSA PRIVATE KEY-----"""
)

d = privkey.d
e = privkey.e
n = privkey.n
print(d, e, n)


def sign(id: int) -> int:
    m = bytes_to_long(f"{id:02d}".encode("utf-8"))
    return pow(m, d, n)


for id in range(2 * 3 * 6):
    sig = sign(id)
    url = f"http://localhost/api/open/{id}"
    params = {"sig": hex(sig)}
    box = requests.get(url, params=params)
    print(box.json())
