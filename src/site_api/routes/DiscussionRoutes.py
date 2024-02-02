import json

from fastapi import APIRouter, Request

from site_api.edgedb import DatabaseFunctions as dbf

discussion_router = APIRouter()


@discussion_router.get("/discussions")
async def get_discussions():
    return await dbf.query(
        "SELECT default::Discussion {**, members: {username, first_name, last_name, id}};"
    )


@discussion_router.get("/discussions/{discussion_id}")
async def get_individual_discussion(discussion_id: int):
    discussion = await dbf.query(
        f"SELECT default::Discussion{{**, members: {{first_name, last_name, username, id}}}} FILTER .discussion_id = {discussion_id};",
        query_single=True,
    )

    if isinstance(discussion, str):
        discussion = json.loads(discussion)

    return discussion


@discussion_router.post("/discussions")
async def make_discussions(request: Request):
    res = await request.json()
    assert res.get("discussion")

    return await dbf.insert_discussion(res.get("discussion"))
