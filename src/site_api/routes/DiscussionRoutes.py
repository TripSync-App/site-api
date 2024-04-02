import json
from typing import Annotated

from fastapi import (APIRouter, Depends, File, HTTPException, Request,
                     UploadFile, status)

from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import Discussion, User
from site_api.routes.utils.LoginUtils import validate_user_token
from site_api.utils import (generate_invite_code, retrieve_thumbnail,
                            upload_thumbnail_image)

discussion_router = APIRouter()


@discussion_router.get("/api/discussions")
async def get_discussions(current_user: Annotated[User, Depends(validate_user_token)]):
    return await dbf.query(
        "SELECT default::Discussion {*, members: {username, first_name, last_name, id}} filter <str>$username in .members.username;",
        username=current_user.username,
    )


@discussion_router.get("/api/discussions/{discussion_id}")
async def get_individual_discussion(
    discussion_id: int, current_user: Annotated[User, Depends(validate_user_token)]
):
    discussion = await dbf.query(
        "SELECT default::Discussion {**, members: {first_name, last_name, username, id}} FILTER .discussion_id = <int64>$discussion_id and <str>$username in .members.username;",
        query_single=True,
        username=current_user.username,
        discussion_id=discussion_id,
    )

    if isinstance(discussion, str):
        discussion = json.loads(discussion)

    return {"discussion": discussion}


@discussion_router.post("/api/discussions/upload-thumbnail")
async def upload_thumbnail(
    _: Annotated[User, Depends(validate_user_token)],
    discussion: Discussion,
    image: UploadFile = File(...),
):
    upload_thumbnail_image(discussion.discussion_id, image)


@discussion_router.get("/api/discussions/thumbnail/{id}")
async def get_thumbnail(
    discussion: Discussion, _: Annotated[User, Depends(validate_user_token)]
):
    return retrieve_thumbnail(discussion.discussion_id)


@discussion_router.post("/api/discussions")
async def make_discussions(request: Request):
    res = await request.json()
    assert res.get("discussion")

    return await dbf.insert_discussion(res.get("discussion"))
