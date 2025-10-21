from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Request
from nats.aio.client import Client as NATS
from nats.errors import TimeoutError as NatsTimeoutError
import json
import os
import random

from nats.js.api import AckPolicy, ConsumerConfig, DeliverPolicy, StreamConfig

nc = NATS()
js = nc.jetstream()


FLAG = os.getenv("FLAG") or "NNS{fake_flag}"
NATS_URL = os.getenv("NATS_URL") or "nats://localhost:4222"

names = ["adam", "jane", "james", "eva", "street"]
messages = ["hiii", ":3", "meow", "hello", "cloud <3", "awesome"]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await nc.connect(NATS_URL)
    print("connected to nats")

    stream_config = StreamConfig(max_msgs_per_subject=50, max_msg_size=5000)
    await js.add_stream(
        stream_config, name="c6f5e1f89e7c434554c38d15d01df51e", subjects=["chat.*"]
    )
    print("nats migration complete")

    for _ in range(random.randint(14, 30)):
        await js.publish_async(
            "chat.admin",
            json.dumps(
                {
                    "author": random.choice(names),
                    "content": random.choice(messages),
                }
            ).encode(),
        )

    await js.publish_async(
        "chat.admin",
        json.dumps(
            {
                "author": "admin",
                "content": f"Wow, you're so CLOUD-NATIVE! Here's your flag: {FLAG}",
            }
        ).encode(),
    )
    for _ in range(random.randint(8, 17)):
        await js.publish_async(
            "chat.admin",
            json.dumps(
                {
                    "author": random.choice(names),
                    "content": random.choice(messages),
                }
            ).encode(),
        )

    yield

    await nc.drain()
    print("disconnected from nats")


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def add_csp_header(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'unsafe-inline' cdn.jsdelivr.net;"
    )
    return response


async def room_messages_generator(room: str, request: Request):
    config = ConsumerConfig(deliver_policy=DeliverPolicy.NEW, ack_policy=AckPolicy.NONE)
    sub = await js.pull_subscribe(room, config=config)
    try:
        while True:
            try:
                if await request.is_disconnected():
                    return
                msg = await sub.fetch(1, timeout=5)
                if len(msg) == 0:
                    continue
                data = msg[0].data.decode()
                yield f"type: message\ndata: {data}\n\n"
            except NatsTimeoutError:
                pass
    finally:
        await sub.unsubscribe()


@app.get("/api/rooms/{room}")
async def get_room(room: str, request: Request):
    if room != "chat.public":
        raise HTTPException(status_code=403, detail="Access denied")

    return StreamingResponse(
        room_messages_generator(room, request), media_type="text/event-stream"
    )


@app.post("/api/rooms/{room}")
async def post_room(room: str, request: Request):
    if "$JS.API" in room:
        raise HTTPException(status_code=403, detail="Sus string detected!")

    body = await request.json()
    reply_to = request.headers["x-nats-reply-to"]
    await nc.publish(room, json.dumps(body).encode(), reply=reply_to, headers={})


app.mount("/", StaticFiles(directory="static", html=True))
