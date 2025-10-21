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
  http://localhost:8000/rpc