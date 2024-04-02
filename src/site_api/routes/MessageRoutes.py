import json
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import User
from site_api.routes.utils.LoginUtils import validate_user_token

message_router = APIRouter()


@message_router.get("/api/messages")
async def get_messages(current_user: Annotated[User, Depends(validate_user_token)]):
    return await dbf.query(
        """
        SELECT default::Message {
        text,
        timestamp,
        discussion: {title},
        vacation := (select .discussion.vacation {name}),
        author: {username, first_name, last_name},
        } filter .author.username = <str>$username order by .timestamp desc;
        """,
        username=current_user.username,
    )


@message_router.get("/api/messages/team")
async def get_team_messages(
    current_user: Annotated[User, Depends(validate_user_token)]
):
    return await dbf.query(
        """
        SELECT default::Message {
        text,
        timestamp,
        discussion: {title},
        vacation := (select .discussion.vacation {name}),
        author: {username, first_name, last_name},
        } filter .author.username != <str>$username and <str>$username in .vacation.members.username order by .timestamp desc;
        """,
        username=current_user.username,
    )


@message_router.get("/api/messages/{message_id}")
async def get_individual_message(message_id: int):
    message = await dbf.query(
        f"SELECT default::Message{{**, author: {{first_name, last_name, username, id}}}} FILTER .message_id = {message_id};",
        query_single=True,
    )

    if isinstance(message, str):
        message = json.loads(message)

    return message


@message_router.post("/api/messages")
async def make_messages(request: Request):
    res = await request.json()
    assert res.get("message")

    return await dbf.insert_message(res.get("message"))
