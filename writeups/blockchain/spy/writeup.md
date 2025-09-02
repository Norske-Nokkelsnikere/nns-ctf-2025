# Challenge Walkthrough: Inspecting Deployed Bytecode

## 1. Checking the Challenge Address

We begin by checking whether there is a contract deployed at the challenge address:

```bash
cast code 0x8389439d8C910bF286ccB6386BFdCDA46899a8b0 \
  --rpc-url https://3560776d-0bfb-4bf6-8ae0-15f628670cef.chall.nnsc.tf/rpc
```

The result is:

```
0x
```

This indicates **no contract is currently deployed** at that address.

---

## 2. Checking the Current Block Number

Next, we check the current block number to understand the blockchain's state:

```bash
cast block-number \
  --rpc-url https://3560776d-0bfb-4bf6-8ae0-15f628670cef.chall.nnsc.tf/rpc
```

This returns:

```
1
```

So we are currently at **block 1** — this is likely a local or custom chain.

---

## 3. Inspecting Block 1

Let’s investigate block 1 for transactions:

```bash
cast block 1 \
  --rpc-url https://3560776d-0bfb-4bf6-8ae0-15f628670cef.chall.nnsc.tf/rpc
```

We find a transaction:

```
transactions: [
  0x1bb3069a68d7adf79d11c23e74a9ad7bc8059fc6bd06a1b26fe9722337a4ba78
]
```

This could be related to our challenge.

---

## 4. Analyzing the Transaction

Let’s get the full transaction details:

```bash
cast tx 0x1bb3069a68d7adf79d11c23e74a9ad7bc8059fc6bd06a1b26fe9722337a4ba78 \
  --rpc-url https://3560776d-0bfb-4bf6-8ae0-15f628670cef.chall.nnsc.tf/rpc
```

Within the output, we find a long `input` field containing raw bytecode:

```
input: 0x608060405234801561000f575f5ffd5b5060405161...
```

This is **contract creation bytecode**, meaning the transaction deployed a contract.

---

## 5. Decompiling the Contract

We paste the bytecode into [ethervm.io](https://ethervm.io/decompile) and observe:

- A valid constructor
- A large block of data appended at the end of the contract

This appended data doesn’t look like executable bytecode — it’s likely **embedded data**.

---

## 6. Decoding Embedded Data

We extract the trailing portion of the bytecode and decode it using [CyberChef](https://gchq.github.io/CyberChef/):

- Apply **Hex Decode** three times

The result is:

```
AAF{1_y0i3_bgf_trgPbagenpgPerngbe_a0j_y3g5_t3g_gu15_c4egl_5g4eg3q_p55736737s6n}
```

This looks like a **scrambled flag**.

---

## 7. Decrypting with Caesar Cipher

The decoded string is Caesar-encrypted. After shifting the characters, we get:

```
NNS{1_l0v3_ots_getContractCreator_n0w_l3t5_g3t_th15_p4rty_5t4rt3d_c55736737f6a}
```

🎉 **Flag recovered!**

---

## 🏁 Final Flag

```
NNS{1_l0v3_ots_getContractCreator_n0w_l3t5_g3t_th15_p4rty_5t4rt3d_c55736737f6a}
```

---

## Notes

- Contract was deployed in block 1
- Flag was embedded in the contract bytecode
- Decoding steps:
  1. Extract bytecode
  2. Hex-decode x3
  3. Caesar decrypt

This challenge tested understanding of low-level Ethereum contract deployment and some CTF-style data hiding techniques.
