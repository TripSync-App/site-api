from typing import Annotated

from fastapi import APIRouter, Depends

from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import AddTeamMembers, Team, User
from site_api.routes.utils.LoginUtils import validate_user_token

team_router = APIRouter()


@team_router.post("/teams")
async def create_team(
    team: Team, current_user: Annotated[User, Depends(validate_user_token)]
):
    if _team := await dbf.create_team(team, current_user):
        return _team


@team_router.post("/teams/add-users")
async def add_users(
    add_team_members: AddTeamMembers,
    current_user: Annotated[User, Depends(validate_user_token)],
):
    print(add_team_members)
