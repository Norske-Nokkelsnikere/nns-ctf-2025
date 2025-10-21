from eth_keys import keys
from eth_utils import keccak

# 1. Private key (replace with your actual key!)
private_key_hex = "0xc9c78e5a1bc52372c0759ed4358f6e4771b379a2ff9b4cc6f1ff898958db3fd5"
private_key_bytes = bytes.fromhex(private_key_hex[2:])
pk = keys.PrivateKey(private_key_bytes)

# 2. Message
message = b"Black Sheep"
msg_hash = keccak(message)

# 3. Sign
sig = pk.sign_msg_hash(msg_hash)
v, r, s = sig.vrs

v += 27

print("msgHash =", "0x" + msg_hash.hex())
print("v =", v)
print("r =", hex(r))
print("s =", hex(s))
print("Your contract call parameters are:")
print(f"""
    withdraw(
        bytes32 msgHash = 0x{msg_hash.hex()},
        uint8 v = {v},
        bytes32 r = 0x{r:064x},
        bytes32 s = 0x{s:064x}
    )
""")
