IMPLEMENTATION=0x8b3ff84Ef7168EE24D3587540167534ed2B1B7A9
RPC_URL=http://localhost:8000/rpc
PRIV_KEY=0xaf76776a10f9a402f7c814acf448d4646d40161af5d79dc617fb81b9d74fc124

cast send $IMPLEMENTATION "callFunction(string)" "nnmwqvd" --private-key $PRIV_KEY --rpc-url $RPC_URL

cast call $IMPLEMENTATION "isSolved()" --rpc-url $RPC_URL