import os
import re
import subprocess
import sys
import time
import json
from contextlib import asynccontextmanager

import httpx
from eth_account import Account
from eth_account.hdaccount import generate_mnemonic
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

Account.enable_unaudited_hdwallet_features()

account_addresses = {}
contract_addresses = {}
is_solved = False
rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
port = os.environ.get("PORT", "1337")
anvil_ip = os.environ.get('ANVIL_IP_ADDR', '0.0.0.0')
client = httpx.AsyncClient()

def gen_accounts_from_mnemonic(mnemonic):
    deployer_acct = Account.from_mnemonic(mnemonic, account_path="m/44'/60'/0'/0/0")
    player_acct = Account.from_mnemonic(mnemonic, account_path="m/44'/60'/0'/0/1")
    return {
        "deployer_private_key": "0x" + deployer_acct.key.hex(),
        "deployer_address": deployer_acct.address,
        "player_private_key": "0x" + player_acct.key.hex(),
        "player_address": player_acct.address,
        "mnemonic": mnemonic,
    }


def start_anvil(mnemonic):
    anvil_cmd = [
        "anvil",
        "--accounts",
        "2",
        "--balance",
        "100",
        "--mnemonic",
        mnemonic,
        "--port",
        "8545",
        "--block-base-fee-per-gas",
        "0",
    ]
    return subprocess.Popen(anvil_cmd)


def cleanup_process(anvil_process):
    if anvil_process.poll() is None:
        anvil_process.terminate()
        try:
            anvil_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            anvil_process.kill()


def signal_handler(anvil_process):
    cleanup_process(anvil_process)
    sys.exit(0)


def deploy_contracts(rpc_url, deployer_account):
    cache_clean_cmd = ["forge", "clean"]
    cache_result = subprocess.run(cache_clean_cmd, capture_output=True, text=True)
    print(f"cache clean result: {cache_result.returncode}")
    if cache_result.stderr:
        print(f"cache clean stderr: {cache_result.stderr}")

    deploy_cmd = [
        "forge",
        "script",
        "script/DeployChallenge.s.sol:DeployChallenge",
        "--ffi",
        "--rpc-url",
        rpc_url,
        "--private-key",
        deployer_account,
        "--broadcast",
    ]
    return subprocess.run(deploy_cmd, capture_output=True, text=True)


def get_addresses(rpc_url):
    try:
        cmd = [
            "forge", "script", "script/GetAddresses.s.sol:GetAddresses",
            "--rpc-url", rpc_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"address extraction failed with return code {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return {}
        
        contracts_json_path = "./contracts.json"
        if os.path.exists(contracts_json_path):
            try:
                with open(contracts_json_path, 'r') as f:
                    content = f.read()
                    print(f"raw contracts.json content: {content}")
                    addresses = json.loads(content)
                
                print(f"loaded addresses from {contracts_json_path}: {addresses}")
                if 'implementation_address' in addresses and 'challenge_address' in addresses:
                    return addresses
                else:
                    print(f"missing required fields in contracts.json. found: {list(addresses.keys())}")
                    return {}
            except Exception as e:
                print(f"error reading contracts.json: {e}")
                return {}
        else:
            print(f"contracts.json file not found at {contracts_json_path}")
            print(f"current working directory: {os.getcwd()}")
            print(f"directory contents: {os.listdir('.')}")
            return {}
        
    except subprocess.TimeoutExpired:
        print("get addresses script timed out")
        return {}
    except json.JSONDecodeError as e:
        print(f"error parsing contracts.json: {e}")
        return {}
    except Exception as e:
        print(f"error running get addresses script: {e}")
        return {}

def check_if_solved():
    global is_solved

    if "implementation_address" not in contract_addresses:
        return {"error": "challenge not deployed yet", "solved": False}
    try:
        cmd = [
            "cast",
            "call",
            contract_addresses["implementation_address"],
            "isSolved()",
            "--rpc-url",
            rpc_url,
        ]
        resp = subprocess.run(cmd, capture_output=True, text=True)
        output = (resp.stdout + resp.stderr).strip()
        challenge_solved = "1" in output
        is_solved = challenge_solved
        response = {
            "solved": challenge_solved,
            "raw_result": resp.stdout.strip()
            if resp.stdout.strip()
            else resp.stderr.strip(),
            "challenge_address": contract_addresses.get("challenge_address", "N/A"),
            "implementation_address": contract_addresses.get(
                "implementation_address", "N/A"
            ),
            "command_success": resp.returncode == 0,
        }
        if challenge_solved:
            flag = os.environ.get("FLAG", "FLAG_NOT_SET")
            response["flag"] = flag
        return response
    except Exception as e:
        is_solved = False
        return {"error": f"exception occurred: {str(e)}", "solved": False}


async def wait_for_anvil(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = await client.post(
                url,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_blockNumber",
                    "params": [],
                    "id": 1,
                },
                timeout=2,
            )
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("timed out waiting for Anvil to start.")


async def check_anvil_health(rpc_url):
    try:
        resp = await client.post(
            rpc_url,
            json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
            timeout=2,
        )
        return resp.status_code == 200
    except Exception:
        return False


async def setup_blockchain():
    global account_addresses, contract_addresses

    print("setting up blockchain...")
    mnemonic = generate_mnemonic(12, "english")
    print(f"generated mnemonic: {mnemonic}")

    accounts = gen_accounts_from_mnemonic(mnemonic)
    account_addresses.update(accounts)

    print(f"player address: {accounts['player_address']}")
    print(f"deployer address: {accounts['deployer_address']}")

    print("starting anvil...")
    anvil_process = start_anvil(mnemonic)

    try:
        print("waiting for anvil to be ready...")
        await wait_for_anvil(rpc_url)
        print("anvil is ready!")

        print("deploying contracts...")
        deploy_output = deploy_contracts(rpc_url, accounts["deployer_private_key"])

        print("deploy command stdout:")
        print(deploy_output.stdout)

        print(f"deploy return code: {deploy_output.returncode}")

        if deploy_output.returncode == 0:
            print("deploy completed successfully!")
            print("extracting addresses...")
            addresses = get_addresses(rpc_url)

            print(f"parsed addresses: {addresses}")

            if addresses:
                contract_addresses.update(addresses)
                print(f"updated contract addresses: {contract_addresses}")
            else:
                print("warning: no contract addresses found in deploy output")
        else:
            print("deploy failed!")

    except Exception as e:
        print(f"error during blockchain setup: {e}")
        import traceback

        traceback.print_exc()

    return anvil_process


@asynccontextmanager
async def lifespan(_app: FastAPI):
    process = await setup_blockchain()

    yield

    cleanup_process(process)


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    from fastapi.responses import FileResponse

    return FileResponse("static/index.html")


@app.get("/api/check_solve")
async def api_check_solve():
    return check_if_solved()


@app.get("/api/info")
async def api_info():
    user_info = {}
    if account_addresses:
        user_info = {
            "player_private_key": account_addresses.get("player_private_key"),
            "player_address": account_addresses.get("player_address"),
        }

    return {
        "user_account": user_info,
        "contract_addresses": contract_addresses,
        "rpc_url": rpc_url,
    }


@app.get("/api/status")
async def api_status():
    global is_solved
    return {
        "status": "running",
        "health": {
            "anvil_healthy": await check_anvil_health(rpc_url),
            "contracts_deployed": bool(contract_addresses),
            "accounts_ready": bool(account_addresses),
        },
        "challenge_solved": is_solved,
        "rpc_url": rpc_url,
        "total_contracts": len(contract_addresses),
        "total_accounts": len(account_addresses),
    }


@app.post("/rpc")
async def rpc_proxy(request: Request):
    rpc_payload = await request.json()
    try:
        response = await client.post(rpc_url, json=rpc_payload)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except Exception as e:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": str(e)},
                "id": rpc_payload.get("id"),
            },
            status_code=500,
        )


@app.get("/health")
async def health():
    return {"status": "healthy"}
