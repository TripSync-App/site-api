from typing import Annotated

from fastapi import APIRouter, Depends

from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import AddTeamMembers, Team, User
from site_api.routes.utils.LoginUtils import validate_user_token

team_router = APIRouter()


@team_router.get("/teams/owned")
async def get_owned_teams(current_user: Annotated[User, Depends(validate_user_token)]):
    return {
        "teams": await dbf.query(
            """
        SELECT default::Team {*} filter .admin_user.username = <str>$username;
        """,
            username=current_user.username,
        )
    }


@team_router.get("/teams/member")
async def get_membered_teams(
    current_user: Annotated[User, Depends(validate_user_token)]
):
    return {
        "teams": await dbf.query(
            """
        SELECT default::Team {*} filter
        .admin_user.username != <str>$username and
        .members.username in array_unpack(<array<str>>[<str>$username]);
        """,
            username=current_user.username,
        )
    }


@team_router.post("/teams")
async def create_team(
    team: Team, current_user: Annotated[User, Depends(validate_user_token)]
):
    if _team := await dbf.create_team(team, current_user):
        return _team


@team_router.post("/teams/add-users")
async def add_users(
    add_team_members: AddTeamMembers,
    _: Annotated[User, Depends(validate_user_token)],
):
    if _team := await dbf.add_team_members(
        add_team_members.team, add_team_members.data
    ):
        return _team
