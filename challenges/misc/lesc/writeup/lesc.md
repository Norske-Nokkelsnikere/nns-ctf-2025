# LE Secure Connections writeup

The challenge has two files in the handout: `lesc.btt` and `netcore.bin`.
The former is a Bluetooth trace from an Ellisys Bluetooth analyser and the latter a readout of the flash of the networking core of an nRF5340 microcontroller.

The Bluetooth trace can be opened in the Ellisys software.
This trace contains communication between a Bluetooth Low Energy central (75:19:9C:73:30:3C) and a peripheral called FlagStore (D8:23:A4:F6:80:8F).

There is encrypted traffic that cannot be read. If you go to View > Security, there is the option to add a key.

This key must be retrieved from the flash readout.

At offset `0x3E000`, the settings API in the Zephyr RTOS which the nRF5340 was running, stores its data. This can be identified by UTF-8 keys like `bt/hash` and `bt/keys`. The payload of a settings value is that which comes before the key. There are two `bt/keys/f0ee10ca62bf0` entries.

```
10113a0000000000000000000000eb571d87351689a7747383b5a75dfde1e1ccda4a0242d07ddbc72ea8c6ab2ed5f87ccda096551c7286ae3f67dcafe596bc434512962b0000000022884018d0a1b68eda89f4f55c58910e0000000003000000
```
and
```
10113a0000000000000000000000e415f9c67e0ec3765266ad876bc713d5e1ccda4a0242d07ddbc72ea8c6ab2ed53c30739c1975a8b660723cbd1e965ba918b6a0f4d1dc00000000ebb06761ee146a61050f8e7098a1cb410000000004000000
```
The latter contains the MAC address of the central (encoded as 3c30739c1975).

The format of the payload is the following struct that can be found in `subsys/bluetooth/host/keys.h` in Zephyr:
```c
struct bt_keys {
	uint8_t id;
	bt_addr_le_t addr;
	uint8_t state;
	uint8_t storage_start[0] __aligned(sizeof(void *));
	uint8_t enc_size;
	uint8_t flags;
	uint16_t keys;
	struct bt_ltk ltk;
	struct bt_irk irk;
#if defined(CONFIG_BT_SIGNING)
	struct bt_csrk local_csrk;
	struct bt_csrk remote_csrk;
#endif /* BT_SIGNING */
#if !defined(CONFIG_BT_SMP_SC_PAIR_ONLY)
	struct bt_ltk periph_ltk;
#endif /* CONFIG_BT_SMP_SC_PAIR_ONLY */
#if (defined(CONFIG_BT_KEYS_OVERWRITE_OLDEST))
	uint32_t aging_counter;
#endif /* CONFIG_BT_KEYS_OVERWRITE_OLDEST */
};
```

We also have
```c
struct bt_ltk {
	uint8_t rand[8];
	uint8_t ediv[2];
	uint8_t val[16];
};

struct bt_irk {
	uint8_t val[16];
	/* Cache for `bt_keys_find_irk`. Not reliable as "current RPA"! */
	bt_addr_t rpa;
};
```

By looking at the `bt_keys_store(struct bt_keys *keys)` function in the same file, we find that the payload starts at `storage_start`.

Addit

We can then parse the payload as:
```
enc_size: 10
flags: 11
keys: 3a00
ltk:
    rand: 0000000000000000
    ediv: 0000
    val: e415f9c67e0ec3765266ad876bc713d5
irk:
    val: e1ccda4a0242d07ddbc72ea8c6ab2ed5
    rpa: 3c30739c1975
```
and so on.

LTK means long-term key. This is the key that is used to encrypt traffic.
By providing the Ellisys software with that key `e415f9c67e0ec3765266ad876bc713d5`, we can decrypt the encrypted traffic.

Inside, there is a read transaction which provides the flag:
`NNS{l3ak1ng_th3_l0ng_t3rm_key_t0_de3rypt_0ld_data}`