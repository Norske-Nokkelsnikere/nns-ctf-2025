from fastapi import FastAPI, Security 
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse, RedirectResponse
import functools
from enum import StrEnum
from pydantic import BaseModel, Field
import typing
import secrets
import os
import asyncio

class CardId(StrEnum):
    EPT_SOCK = "ept_sock"
    EPT_STICKER = "ept_sticker"
    FLAG = "flag"


class Card(BaseModel):
    id: CardId
    price: int
    description: str

@functools.cache
def get_all_cards() -> list[Card]:
    return [
        Card(
            id=CardId.EPT_SOCK,
            price=50,
            description="Makes you better at making CTF challenges"
        ),
        Card(
            id=CardId.EPT_STICKER,
            price=100,
            description="hold on let me come back with some stickers - nordbo, who never returned"
        ),
        Card(
            id=CardId.FLAG,
            price=100_000,
            description="Flags are cool"
        )
    ]
@functools.cache
def get_card_by_id(id: CardId) -> Card:
    cards = get_all_cards()
    for card in cards:
        if card.id == id:
            return card
    raise AssertionError("unreachable")
@functools.cache
def create_default_cards() -> list[CardId]:
    return [
        CardId.EPT_SOCK
    ]

class Account(BaseModel):
    cards: typing.Annotated[list[CardId], Field(default_factory=create_default_cards)]
    is_testing_card: bool = False
    balance: int = 100

app = FastAPI()
app.mount("/ui", StaticFiles(directory="ui", html=True))
FLAG = os.getenv("FLAG", "try again, but in production!")
auth_security = typing.Annotated[str, Security(APIKeyHeader(name="Token"))]
ACCOUNTS: dict[str, Account] = {}

@app.get("/")
async def redirect_to_ui():
    return RedirectResponse("/ui/")

@app.post("/accounts/@me")
async def create_account():
    token = secrets.token_hex()
    account = Account()
    ACCOUNTS[token] = account
    return {
        "token": token
    }
@app.get("/accounts/@me")
async def get_current_account(token: auth_security) -> Account:
    return ACCOUNTS[token]


@app.get("/flag")
async def get_flag(token: auth_security):
    account = ACCOUNTS[token]
    if account.is_testing_card:
        return JSONResponse({"detail": "nice try :)"}, status_code=400)

    if not CardId.FLAG in account.cards:
        return JSONResponse({"detail": "get the flag first :)"}, status_code=400)

    
    return FLAG

@app.post("/cards/{card_id}/test")
async def test_card(card_id: CardId, token: auth_security):
    account = ACCOUNTS[token]

    if account.is_testing_card:
        return JSONResponse({"detail": "already testing something else"}, status_code=400)
    if card_id in account.cards:
        return JSONResponse({"detail": "you already own this"}, status_code=400)
    
    account.is_testing_card = True
    account.cards.append(card_id)
    # you get 5 seconds to view your fancy profile
    async def revoke_test_card():
        await asyncio.sleep(5)
        account.cards.remove(card_id)
        account.is_testing_card = False
    asyncio.create_task(revoke_test_card())
@app.post("/cards/{card_id}/buy")
async def buy_card(card_id: CardId, token: auth_security):
    account = ACCOUNTS[token]

    if card_id in account.cards:
        # TODO: Cancel test when user wants to buy
        return JSONResponse({"detail": "you already have this"}, status_code=400)

    card = get_card_by_id(card_id)
    if account.balance - card.price < 0:
        return JSONResponse({"detail": "you need more money"}, status_code=400)
    account.balance -= card.price
    
    account.cards.append(card_id)

@app.get("/cards")
async def get_cards() -> list[Card]:
    return get_all_cards()
