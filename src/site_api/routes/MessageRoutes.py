import json

from fastapi import APIRouter, Request

from site_api.edgedb import DatabaseFunctions as dbf

message_router = APIRouter()


@message_router.get("/messages")
async def get_messages():
    return await dbf.query("SELECT default::Message {**};")


@message_router.get("/messages/{message_id}")
async def get_individual_message(message_id: int):
    message = await dbf.query(
        f"SELECT default::Message{{**}} FILTER .message_id = {message_id};",
        query_single=True,
    )

    if isinstance(message, str):
        message = json.loads(message)
        message["author"].pop("password")

    return message


@message_router.post("/messages")
async def make_messages(request: Request):
    res = await request.json()
    assert res.get("message")

    return await dbf.insert_message(res.get("message"))
