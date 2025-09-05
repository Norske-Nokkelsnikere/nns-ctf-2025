# Translator, not clanker - Writeup

## Files related to solving the challenge are in this writeup's root folder

**Author: Taokyle - THEM?!**

OS: I have skill issue, kept falling into rabbit holes (details not included in this writeup cuz Im too ashamed)

## Situation

Translator, not clanker

fslaktern - 375 pts (28 solves)

I AM A TRANSLATOR. GIVE ME A WORD AND I WILL TRANSLATE. GIVE ME A LIFE STORY AND I WILL TRANSLATE. GIVE ME NOTHING AND I WILL NOT UNDERSTAND WHAT YOU MEAN, NOT BECAUSE I AM DUMB, BUT BECAUSE I DO NOT WANT TO UNDERSTAND. CALL ME A CLANKER AND I WILL UPSET YOU IN WAYS THAT YOU CAN NOT COMPREHEND, YET.

Attachments:\
[translator-not-clanker.tar.gz -> encode-redacted.py](./encode-redacted.py)

## The Beginning

First, we are going to take a look at the "source" provided

```py
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

```

it seems that this chal is a grey box, since some important parts are redacted.

However, we can see that it should be **splitting** the inputted message **by spaces**, and convert each of them into **base64** before printing them out.

## The Beginning - checkpoint Q&A

Q - What do LGTM and RTFM mean?\
A - LGTM probably means "Looks Good To Me", and RTFM probably means "Read The Fucking Manual".\
I searched them up, and it seems that a new word will appear in my code soon lol

Q - What is Base64?\
A - Base64 is a way to represent any bit sequence in the form of `a-z`, `A-Z`, `0-9`, and 2 customizable symbols (usually `+/`)\
It works by transforming any given sequence into bits, and then seperating them every 6 bits. That way, they can be represented by just (2**6=)64 printable ascii characters.\
For more info, go check out [this wikipedia page](https://en.wikipedia.org/wiki/Base64)

## Leaking codes

well since this is a grey box that allows user input, we can always try to **raise errors** somewhere for more info.

By spamming random special characters, I got this error from the server

``` None
Traceback (most recent call last):
  File "/encode.py", line 55, in <module>
    base64 = convert(words)
  File "/encode.py", line 46, in convert
    based = b64e(w.encode("utf-8"), flag_bits[i * 4 : i * 4 + 4])
                 ~~~~~~~~^^^^^^^^^
UnicodeEncodeError: 'utf-8' codec can't encode character '\udc9b' in position 1: surrogates not allowed
```

Now we know some more things about the code.

First, it seems that the flag will go through the unused `as_bits()` function, as its name is now *flag_bits* instead of *FLAG*.\
Then, the word (assumed from *w* in `w.encode()`) will go through some operations with the flag bits before/after converting it into base64.

There also exists a variable *i*, assumed to be short for **index**, which means that there would be some difference for every word.

## Leaking codes - checkpoint Q&A

Q - arnt the content provided from the leaked code alr in `b64e(data: bytes, flag_bits: str)`?\
A - Yeah no, the flag bits part is quite important imo, as we then know the flag is being split across words

## Base64

I've actually done a small trivia on base64 for my teammates

------

Have you ever wondered what the `=` do in base64, why its always at the end, and why sometimes theres 1 sometimes theres 2, and sometimes none?\
Well if you have looked at the base64 tip above, you can notice base64 is a **sextet** *(base 6)* encoding while ascii is **octet** *(base8)*.\
If you can do simple ratio simplifications, you can realize the **ratio** of base64:ascii is **3:4**, which every 4 base64 chars == 3 ascii chars.

```None
        1       2       3    
8-bit:  111111112222222233333333
Base64: 111111222222333333444444
        1     2     3     4     
```

So, what if the total chars in ascii is **not** divisible by 3? We can't just leave random hanging misaligned bits??\
Well, we can place 0s at the end (A=`000000`), but then there would be some extra `\0` at the end of the message after decoding\
(there's `XXXXXX` `XX`|`0000` `0000`|`00` `000000`, which is char+`\0\0`. OR there's `XXXXXX` `XX`|`XXXX` `XXXX`|`00` `000000`, which is char+char+`\0`).

Thats why `=` is here. It's purpose is to pad the base64 chars so that the total b64len is divisible by 4, and can decoded into full ascii characters.\
When you see `=`, it means that the **4 sextet** chunk will be decoded to **2 octet** chunks only (2 ascii char), and the rest of the bytes are ignored.\
When you see `==`, it means that the **4 sextet** chunk will be decoded to **1 octet** chunks only, and the rest of the bytes are ignored.

Also thats why if you paid attention, all base64 messages' length is divisible by 4 after being padded with `=`s\
Thats just to tell your base64 decoder not to panic when theres leftover bits

------

However, when you input some random things (for example, part of the given prompt)

```None
< I AM A TRANSLATOR. GIVE ME A WORD AND I WILL TRANSLATE.
> SU== QU3= QU== VFJBTlNMQVRPUi7= R0lWRV== TUU= QX== V09SRL== QU5E=== ST== V0lMTH== VFJBTlNMQVRFLk==
```

you can notice some triple `=`s, which means that the last **4 sextet** chunk will be decoded to **0 octet** chunks.

or in other words, the last 3 sextet chunk will be **ignored**, causing the first octet chunk to be **incomplete**, resulting into a **0 octet chunks** output.

```None
        1
8-bit:  111111??XXXXXXXXXXXXXXXX
Base64: 111111XXXXXXXXXXXXXXXXXX
        1     =     =     =     
```

This should **NOT** happen if the base64 is normally encoded, but its here! What does it imply? Something, some `<8` bits raw bits got mixed into the base64.\
And since decoding the output base64 gives the input message quite well, the extra bits, assumed to be the 4 bits flag bits, is appended to the last 4 bits of the base64 input right before the conversion.

## Base64 - checkpoint Q&A

Q - Why won't 3 `=`s appear if the base64 is normally encoded?\
A - base64encode will take in some bytes and encode their bits into base64, Every byte must be 8 bits (by definition) so there would be no case where a byte with 6 bits appear.\
Unless a bits object is provided instead of bytes (aka there are extra/missing bits after the bytes->bits conversion). We know there arn't missing bits, mentioned above, so we know there are extra bits laying around.

## Extracting the flag

Now we know that the extra 4 bits are the flag bits, we can now spam the same message over and over to extract the full flag bits

```None
< a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a
> YU== Ye== YU== Ye== YV== YT== YX== Yb== YX== YT== YX== YU== YW== Yf== YX== YQ== YV== Yf== YW== YT== YT== YU== YW== Yc== YW== Yc== YT== YR== YW== Ye== YW== YX== YV== Yf== YW== Yd== YT== YT== YV== Yf== YW== YT== YW== Yc== YT== YU== YW== Ye== YW== Yb== YT== YT== YX== YS== YV== Yf== YT== YT== YT== YS== YT== YS== YW== YV== YW== YS== YW== YS== YT== YS== YW== YT== YW== YT== YW== YU== YW== YT== YT== YW== YX== Yd== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y===
```

We can see that there are alot of `Y===`s at the end, implying the full flag had been extracted and what remains is just base64encode of `a`, so now we can use a simple python program to stitch the bits together

```py
>>> b64 = {c: i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")}
>>> 
>>> def f(x):
...     if x[1] == '=': return ""
...     x = (b64.get(x[0])<<6) | b64.get(x[1]) & 0b1111
...     return format(x, 'x')
... 
```

*f(x) takes in a base64 encoded word and takes its first 2 bytes (we know the flag lies in the first 2 bytes cause the 3rd and 4th byte in every word received is a pad `=`)*\
*then, if it contains flag bits (not `Y===`, aka the second byte is not pad `=`), it converts the word back to binary*\
*(`(b64.get(x[0])<<6)` to grab the first 6 bits and move it 6 bits upward to leave the bottom 6 bits for the next byte*\
*`b64.get(x[1])` to grab the second 6 bits, `|` adds these 6 bits chunks together, stitching into 12 bits)*\
*Now, since we know the flag is probably appended behind the original word, and is 4 bits long, we do `& 0b1111` to grab the last 4 bits out*\
*Finally, we return the extracted flag bits as hex (not as binary to reduce the length when printing it out later)*

```py
>>> inp = "YU== Ye== YU== Ye== YV== YT== YX== Yb== YX== YT== YX== YU== YW== Yf== YX== YQ== YV== Yf== YW== YT== YT== YU== YW== Yc== YW== Yc== YT== YR== YW== Ye== YW== YX== YV== Yf== YW== Yd== YT== YT== YV== Yf== YW== YT== YW== Yc== YT== YU== YW== Ye== YW== Yb== YT== YT== YX== YS== YV== Yf== YT== YT== YT== YS== YT== YS== YW== YV== YW== YS== YW== YS== YT== YS== YW== YT== YW== YT== YW== YU== YW== YT== YT== YW== YX== Yd== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y=== Y==="
>>> 
>>> out = ""
>>> 
>>> for i in inp.strip().split():
...    out += f(i)
...
>>> out
'4e4e537b73746f705f63346c6c316e675f6d335f636c346e6b33725f3133306162353030633661357d'
>>> long_to_bytes(0x4e4e537b73746f705f63346c6c316e675f6d335f636c346e6b33725f3133306162353030633661357d)
b'NNS{stop_c4ll1ng_m3_cl4nk3r_130ab500c6a5}'
```

then you will get the

### Flag

`NNS{stop_c4ll1ng_m3_cl4nk3r_130ab500c6a5}`

## Extracting the flag - checkpoint Q&A

Q - why interactive python?\
A - Its fast to call and write and debug, so why not?

## Aftermath

I fell into so many rabbit holes while solving this chal, such as the program ignoring "clanker" in any case

By the way, if anyone want it, the source code running on the server is at [encode.py](./encode.py), provided by the author *fslaktern*

From this challenge I learned

* what is **RTFM** (will use it in my code lmao)
* weird ahh 3 `=`s base64

## Aftermath - checkpoint Q&A

Q - :moyai:\
A - I don't think you need a Q&A for aftermath lol