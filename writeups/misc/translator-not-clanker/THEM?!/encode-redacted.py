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


# LGTM
def get_input() -> list[str]:
    print(PROMPT, end="\n\n")
    return input("< ").strip().split()


# LGTM
def convert(words: list[str]) -> list[str]:
    # REDACTED
    raise NotImplementedError


# RTFM
def b64e(data: bytes, flag_bits: str) -> str:
    # REDACTED
    raise NotImplementedError


# LGTM
if __name__ == "__main__":
    while True:
        words = get_input()
        base64 = convert(words)

        print(">", " ".join(base64), end="\n\n")