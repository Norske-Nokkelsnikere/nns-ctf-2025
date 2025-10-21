CONTRACT=0x97176B8ec1D1070B53A835f86a4FF0746582430F
RPC_URL=https://95b4f46b-cba2-41f1-ba89-cb0fa5d9f7c3.chall.dev.nnsc.tf/rpc

HASH=$(cast rpc ots_getContractCreator $CONTRACT --rpc-url $RPC_URL | jq -r .hash)

cast tx $(cast rpc ots_getContractCreator $CONTRACT --rpc-url $RPC_URL | jq -r .hash) --rpc-url $RPC_URL --json | jq -r .input