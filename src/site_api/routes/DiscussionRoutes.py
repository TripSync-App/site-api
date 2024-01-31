from fastapi import APIRouter, Request

from site_api.edgedb import DatabaseFunctions as dbf

discussion_router = APIRouter()


@discussion_router.get("/discussions")
async def get_discussions():
    return await dbf.query("SELECT default::Discussion {**};")


@discussion_router.post("/discussions")
async def make_discussions():
    ...
