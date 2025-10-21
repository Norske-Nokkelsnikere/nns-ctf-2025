from pydantic import BaseModel
from typing import Any

class CreateAccountSchema(BaseModel):
    username: str
    flag: str | None = None

class CreateAccountResponse(BaseModel):
    user_id: int
    token: str

class GetFeedResponse(BaseModel):
    next_fetch_after_seconds: float
    notifications: list[Any]

class SendMessageSchema(BaseModel):
    content: str