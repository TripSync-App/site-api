from fastapi import APIRouter, Request

from site_api.edgedb import DatabaseFunctions as dbf

message_router = APIRouter()


@message_router.get("/messages")
async def get_messages():
    return await dbf.query("SELECT default::Message {**};")


@message_router.post("/messages")
async def make_messages():
    ...
