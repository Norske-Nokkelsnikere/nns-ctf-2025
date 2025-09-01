#!/usr/bin/env python3

import os
from string import ascii_lowercase, ascii_uppercase, digits

# LGTM
BASE64 = ascii_uppercase + ascii_lowercase + digits + "+/"
FLAG = os.environ["FLAG"].encode("utf-8")
PROMPT = "I AM A TRANSLATOR. GIVE ME A WORD AND I WILL TRANSLATE. GIVE ME A LIFE STORY AND I WILL TRANSLATE. GIVE ME NOTHING AND I WILL NOT UNDERSTAND WHAT YOU MEAN, NOT BECAUSE I AM DUMB, BUT BECAUSE I DO NOT WANT TO UNDERSTAND. CALL ME A CLANKER AND I WILL UPSET YOU IN WAYS THAT YOU CAN NOT COMPREHEND, YET."


# LGTM
def as_bits(b: bytes) -> str:
    return "".join(f"{c:08b}" for c in b)


# RTFM
def b64e(data: bytes, flag_bits: str) -> str:
    bits = as_bits(data) + flag_bits
    flagged_bits = bits[: len(bits) - (len(bits) % 6)]
    assert len(flagged_bits) % 6 == 0

    output = ""
    for i in range(0, len(flagged_bits), 6):
        part = flagged_bits[i : i + 6]
        output += BASE64[int(part, 2)]

    output += "==="[: 4 - (len(output) % 4)]
    return output


# LGTM
def get_input() -> list[str]:
    print(PROMPT, end="\n\n")
    return input("< ").strip().split()


# LGTM
def convert(words: list[str]) -> list[str]:
    flag_bits = as_bits(FLAG)
    converted = []
    for i, w in enumerate(words):
        if w.lower() == "clanker":
            continue

        based = b64e(w.encode("utf-8"), flag_bits[i * 4 : i * 4 + 4])
        converted.append(based)
    return converted


# LGTM
if __name__ == "__main__":
    while True:
        words = get_input()
        base64 = convert(words)

        print(">", " ".join(base64), end="\n\n")