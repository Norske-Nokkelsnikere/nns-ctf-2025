# infra-base

move to the src directory
```bash 
cd src
```
build the challenge
```bash
docker compose up --build
```

interact with the challenge at:
```bash
http://localhost:5000
```

api endpoints:
```bash
http://localhost:5000/api/check_solve
http://localhost:5000/api/info
http://localhost:5000/api/status
http://localhost:5000/health
```
where:
- check_solve: check if the challenge is solved
- info: get the account and contract addresses
- status: get the health information and challenge status
- health: health check

in another terminal, check the challenge state from the implementation contract with this cast command:
```bash
cast call <IMPLEMENTATION_ADDRESS> "isSolved()" --rpc-url http://127.0.0.1:8545
```

---

to test if rpc url is reachable from your machine, run these commands:
```bash
cast block-number --rpc-url http://127.0.0.1:8545
```

or 
```bash
curl -s -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' http://localhost:8545
```

rpc url is binded to 0.0.0.0, so you can access it from your machine