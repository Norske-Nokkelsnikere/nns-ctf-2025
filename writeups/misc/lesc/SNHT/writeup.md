# LE Secure Connections - NNS CTF 2025

Challenge Author: simen e

Writeup Author: Lucas Drufva


The challenge **LE Secure Connections** involved analyzing Bluetooth Low Energy (BLE) traffic that was known to contain a flag. The capture itself, however, was encrypted. The provided hint suggested that the key material might still be retrievable from the firmware of one of the communicating devices.

## Understanding BLE Encryption

In BLE secure connections, the **Long Term Key (LTK)** is created during pairing via **ECDH**. The LTK is then used to derive the **session key (SK)** together with values sent during the link setup (such as the random number inside an `ENCRYPT_REQ`). The SK is then applied in **AES-CCM** to protect link layer traffic.

When devices choose to bond, the LTK and related data are written to persistent memory. Upon reconnection, they can skip the ECDH procedure and simply reuse the stored key material. This behavior was critical to the challenge: by extracting the LTK from the device’s flash, we could decrypt the sniffed traffic.

## Flash Dump Analysis

The challenge provided a flash dump of an **nRF52**-based embedded system. Running `strings` immediately revealed the software stack:

```
*** Booting nRF Connect SDK v2.9.0-7787b2649840 ***
*** Using Zephyr OS v3.7.99-1f8f3dc29142 ***
```

Thus, the system was running **Zephyr OS** with the **nRF Connect SDK**.

In Zephyr, Bluetooth keys are persisted by the `settings` subsystem. Looking at the implementation in [`zephyr/subsys/bluetooth/host/keys.c`](https://github.com/zephyrproject-rtos/zephyr/blob/main/subsys/bluetooth/host/keys.c), the relevant function is `bt_keys_store`, which writes bonding data into storage under keys of the form:

```
bt/keys/<addr><type>
```

## Locating the Key Record

Searching the flash dump for `bt/keys` revealed a record:

```
bt/keys/f0ee10ca62bf0
```

The suffix `0` indicates that this refers to a **public address** (IEEE-assigned, permanent). Although the sniffed traffic showed randomized private addresses, this distinction was expected: the bonded address still appears in persistent storage.

The record was found near the end of flash, surrounded by erased regions, strongly indicating that this was a writable storage section used by Zephyr’s settings subsystem.

## Determining the Backend: FCB vs NVS

Zephyr supports two backends for storing settings:

* **Flash Circular Buffer (FCB):** ASCII entries like `wifi/ssid=myNetwork`
* **Non-Volatile Storage (NVS):** Binary records with an allocation table (ATE)

In the dump, no ASCII `=` delimiters were present around the `bt/keys` entry, ruling out FCB. Inspecting the memory layout showed binary data starting at `0x03E000` with additional structures at the end of the sector (`0x03EF00`), consistent with **NVS**.


## Parsing NVS

The flash sector was extracted:

```bash
dd if=netcore.bin of=NVS.bin skip=$((0x3E000)) count=$((0x800)) bs=1
python3 nvs.py NVS.bin 0x3e000
```

Using the provided [`nvs.py`](./nvs.py), the ATE table was successfully reconstructed:

```
Idx   Address    ID  Off  Len  Prt   CRC    OK
---  --------  ----  ---  ---  ---  ----  ----
 12  0x03E790  8002  256   21  255  0x96  True
 11  0x03E798  C002  160   96  255  0xA2  True
 10  0x03E7A0  8000  156    2  255  0xBE  True
  9  0x03E7A8  8000  152    2  255  0x31  True
  8  0x03E7B0  C002  152    0  255  0x28  True
  7  0x03E7B8  8002  152    0  255  0x5E  True
  6  0x03E7C0  8002  128   21  255  0x17  True
  5  0x03E7C8  C002   32   96  255  0x35  True
  4  0x03E7D0  8000   28    2  255  0x29  True
  3  0x03E7D8  8001   20    7  255  0x2F  True
  2  0x03E7E0  C001    4   16  255  0xDF  True
  1  0x03E7E8  8000    0    2  255  0x8D  True
  0  0x03E7F0  FFFF    0    0  255  0x5C  True
```

The valid CRCs confirmed that NVS was being used.

## Reconstructing Zephyr Settings

Each setting is stored as two NVS entries, it is essentially building key-value storage by pairing up two entries inside flash: one for the setting’s name and one for its value. NVS itself only uses IDs to index blobs of data. For each setting, the name is stored at some ID X (startig at NVS_NAMECNT_ID 0x8000), and the value is stored at ID X plus a fixed offset reserved for values (NVS_NAME_ID_OFFSET 0x4000). 

Using [`settings.py`](./settings.py), the sector was reconstructed into human-readable settings:

```
bt/keys/f0ee10ca62bf0
    (old-0, 96 B)
        10 11 3A 00 ... 04 00 00 00
    (current, 96 B)
        10 11 3A 00 ... 03 00 00 00

bt/hash
    (current, 16 B)
        50 14 DE 2D 97 51 BD 56 D8 15 EE 21 76 4C 4B E6
```

Here, the 96-byte blobs bt/keys/f0ee10ca62bf0 represented serialized `struct bt_keys` objects.

## Decoding the Key Structure

To parse the data, the structure definitions from Zephyr were recreated. From [`zephyr/subsys/bluetooth/host/keys.h`](https://github.com/zephyrproject-rtos/zephyr/blob/main/subsys/bluetooth/host/keys.h):

```c
struct bt_ltk {
    uint8_t rand[8];
    uint8_t ediv[2];
    uint8_t val[16];
};

struct bt_irk {
    uint8_t val[16];
    bt_addr_t rpa;
};

struct bt_keys {
    uint8_t id;
    bt_addr_le_t addr;
    uint8_t state;
    uint8_t storage_start[0] __attribute__((aligned(sizeof(void *))));
    uint8_t enc_size;
    uint8_t flags;
    uint16_t keys;
    struct bt_ltk ltk;
    struct bt_irk irk;
    struct bt_ltk periph_ltk;
};
```

A small parser program ([`keys.c`](./keys.c)) was used to map the 96-byte blob onto this struct and print the relevant values:

```bash
gcc keys.c -o keys
./keys
```

Output:

```
LTK: E415F9C67E0EC3765266AD876BC713D5
IRK: E1CCDA4A0242D07DDBC72EA8C6AB2ED5
```

## Decrypting the Traffic

With the **LTK** extracted, it was now possible to load it into a Bluetooth protocol analyzer such as **Ellisys**. Providing the key enabled full decryption of the sniffed traffic, and the plaintext revealed the flag.