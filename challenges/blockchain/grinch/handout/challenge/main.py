import os
import subprocess
import sys
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
port = int(os.environ.get("PORT", "1337"))
client = httpx.AsyncClient()

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


def start_anvil():
    anvil_cmd = [
        "anvil",
        "--accounts",
        "0",
        "--port",
        "8545",
    ]
    return subprocess.Popen(anvil_cmd)


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


async def setup_blockchain():
    print("setting up blockchain...")
    print("starting anvil with 0 accounts...")
    anvil_process = start_anvil()

    try:
        print("waiting for anvil to be ready...")
        await wait_for_anvil(rpc_url)
        print("anvil is ready!")

    except Exception as e:
        print(f"error during blockchain setup: {e}")
        import traceback

        traceback.print_exc()
        cleanup_process(anvil_process)
        print("anvil setup failed, exiting...")
        sys.exit(1)

    return anvil_process


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


@app.get("/api/check_anvil")
async def api_check_anvil():
    try:
        resp = await client.post(
            rpc_url,
            json={"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []},
            timeout=5,
        )
        
        result = resp.json()
        block_number = result.get("result", "0x0")
        block_num_decimal = int(block_number, 16) if block_number.startswith("0x") else block_number
        
        return {
            "anvil_healthy": True,
            "block_number": block_num_decimal,
            "rpc_url": rpc_url
        }
            
    except Exception as e:
        flag = os.environ.get("FLAG", "FLAG_NOT_SET")
        return {
            "anvil_healthy": False,
            "error": str(e),
            "rpc_url": rpc_url,
            "flag": flag,
            "solved": True
        }


@app.get("/api/info")
async def api_info():
    return {
        "bob_address": None,
        "user_address": None,
        "user_private_key": None,
        "rpc_url": rpc_url,
    }


@app.get("/api/status")
async def api_status():
    anvil_healthy = await check_anvil_health(rpc_url)
    challenge_solved = not anvil_healthy
    
    return {
        "status": "running",
        "health": {
            "anvil_healthy": anvil_healthy,
            "accounts_ready": False,
            "challenge_solved": challenge_solved,
        },
        "rpc_url": rpc_url,
        "total_accounts": 0,
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
