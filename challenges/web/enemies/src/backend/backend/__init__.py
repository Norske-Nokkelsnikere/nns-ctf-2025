from fastapi import FastAPI
import sqlite3
import os
from itsdangerous import URLSafeSerializer
from .models import CreateAccountResponse, CreateAccountSchema, GetFeedResponse, SendMessageSchema
import json
from hashlib import sha256
from os import environ

APP = FastAPI()
DB = sqlite3.connect("app.sqlite")
DB.row_factory = sqlite3.Row
FLAG = environ.get("FLAG", "NNS{demo-flag}")

# Tokens
SECRET = environ.get("SECRET", os.urandom(32))
SIGNER = URLSafeSerializer(SECRET)

# Config
FEED_LIMIT: int = 100

def setup_db():
    with open("setup.sql") as f:
        DB.executescript(f.read())

setup_db()

@APP.options("/{path:path}")
async def handle_options(path: str):
    del path # Unused
    return "OK"
@APP.post("/users/@me")
async def create_account(schema: CreateAccountSchema) -> CreateAccountResponse:
    admin = False
    if schema.flag is not None:
        if sha256(schema.flag.encode()).digest() == sha256(FLAG.encode()).digest():
            admin = True

    cursor = DB.execute("insert into users (username, admin) values (?, ?) returning (id)", [schema.username, admin])
    row = cursor.fetchone()
    token = SIGNER.dumps({"user_id": row["id"]})
    notification = {
        "type": "user_create",
        "data": {
            "user_id": row["id"],
            "username": schema.username,
            "admin": admin
        }
    }
    DB.execute("insert into notifications (user_id, content) values (null, ?)", [json.dumps(notification)])
    DB.commit()
    return CreateAccountResponse(
        token=token,
        user_id=row["id"]
    )
@APP.post("/users/{user_id}/messages")
async def send_message(user_id: int, token: str, schema: SendMessageSchema) -> None:
    token_info = SIGNER.loads(token)
    sender_user_id = token_info["user_id"]
    notification = {
        "type": "message",
        "data": {
            "sender": {
                "user_id": sender_user_id
            },
            "recipient": {
                "user_id": user_id
            },
            "content": schema.content
        }
    }
    serialized_notification = json.dumps(notification)
    DB.execute("insert into notifications (user_id, content) values (?, ?), (?, ?)", [sender_user_id, serialized_notification, user_id, serialized_notification])
    DB.commit()



@APP.get("/feed")
async def get_feed(token: str, last_seen_notification: int | None = None) -> GetFeedResponse:
    token_info = SIGNER.loads(token)
    user_id = token_info["user_id"]
    if last_seen_notification is None:
        cursor = DB.execute("select * from notifications where user_id is null or user_id = ? limit ?", [user_id, FEED_LIMIT])
    else:
        cursor = DB.execute("select * from notifications where (user_id is null or user_id = ?) and id > ? limit ?", [user_id, last_seen_notification, FEED_LIMIT])

    notifications = [
        {
            **json.loads(notification["content"]),
            "id": notification["id"]
        }
        for notification in cursor.fetchall()
    ]
    return GetFeedResponse(
        next_fetch_after_seconds=[1, .1][len(notifications) == FEED_LIMIT],
        notifications=notifications
    )
    
