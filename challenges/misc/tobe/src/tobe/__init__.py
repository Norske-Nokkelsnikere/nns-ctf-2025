from fastapi import FastAPI, WebSocket
import os
import asyncio
from uuid import uuid4
import sys
import ast

from fastapi.responses import FileResponse

app = FastAPI()
FLAG = os.getenv("FLAG", "only-available-in-production")

async def is_key_valid(key: str) -> bool:
    if len(key) != 10:
        return False
    
    if not await test(key[0]*5):
        return False
    if not await test(key[0]*25):
        return False
    if not await test(key[1]):
        return False
    if await test(key[0] + key[1]):
        return False
    if await test(key[2]):
        return False
    if await test2(key[3:]):
        return False
    
    return True

async def test(text: str) -> bool:
    code = f"import hikari\nprint(eval(repr({repr(text)})) is eval(repr({repr(text)})))"
    return await test_in_seperate_process(code)

async def test2(text: str) -> bool:
    return await test_in_seperate_process(f"import hikari,sys\ntext = ({repr(text)} + \"a\")[:-1]\nprint(text is sys.intern(text))")

async def test_in_seperate_process(code: str) -> bool:
    # NOTE: Trying to remove the process seperation *will* change the logic. don't bother :)
    file_name = f"/tmp/{uuid4()}.py"
    with open(file_name, "w+") as f:
        f.write(code)
    
    process = await asyncio.create_subprocess_exec(sys.executable, file_name, stdout=asyncio.subprocess.PIPE)
    stdout, _stderr = await process.communicate()
    out = stdout.decode().strip()
    return ast.literal_eval(out)


@app.get("/")
async def get_index():
    return FileResponse("index.html")

@app.websocket("/flag")
async def key_websocket(ws: WebSocket) -> None:
    await ws.accept()
    key = await ws.receive_text()
    if await is_key_valid(key):
        await ws.send_text(FLAG)
    else:
        await ws.send_text("invalid key")
