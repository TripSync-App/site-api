from typing import Annotated

from fastapi import APIRouter, Depends, Request

from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import (AddTeamMembers, BaseTeam,
                                           InviteCode, RemoveTeamMember, Team,
                                           User)
from site_api.routes.utils.LoginUtils import validate_user_token
from site_api.utils import generate_invite_code

team_router = APIRouter()


@team_router.get("/api/teams/owned")
async def get_owned_teams(current_user: Annotated[User, Depends(validate_user_token)]):
    teams = {
        "teams": await dbf.query(
            """
        SELECT default::Team {*, admin_user: {username}, vacations: {**}, discussions: {**}, members: {user_id, username, first_name, last_name}} filter .admin_user.username = <str>$username;
        """,
            username=current_user.username,
        )
    }
    return teams


@team_router.get("/api/teams/member")
async def get_membered_teams(
    current_user: Annotated[User, Depends(validate_user_token)],
):
    return {
        "teams": await dbf.query(
            """
        SELECT default::Team {*, admin_user: {username, first_name, last_name}, members: {first_name, last_name}} filter
        .admin_user.username != <str>$username and
        .members.username in array_unpack(<array<str>>[<str>$username]);
        """,
            username=current_user.username,
        )
    }


@team_router.post("/api/teams")
async def create_team(
    team: Team, current_user: Annotated[User, Depends(validate_user_token)]
):
    if _team := await dbf.create_team(team, current_user):
        return _team


@team_router.post("/api/teams/add-users")
async def add_users(
    add_team_members: AddTeamMembers,
    _: Annotated[User, Depends(validate_user_token)],
):
    if _team := await dbf.add_team_members(
        add_team_members.team, add_team_members.data
    ):
        return _team


@team_router.post("/api/teams/remove-user")
async def remove_user(
    remove_team_members: RemoveTeamMember,
    user: Annotated[User, Depends(validate_user_token)],
):
    if _team := await dbf.remove_team_member(remove_team_members.team, user):
        return _team


@team_router.post("/api/teams/create-invite")
async def create_invite(
    team: BaseTeam,
    _: Annotated[User, Depends(validate_user_token)],
):
    code = generate_invite_code()
    if _team := await dbf.create_invite(team=team, code=code):
        return _team


@team_router.post("/api/teams/get-invite")
async def get_invite(
    team: BaseTeam,
    request: Request,
    _: Annotated[User, Depends(validate_user_token)],
):
    invite_code = await dbf.get_invite(team=team)
    if invite_code:
        base_url = str(request.url)
        base_url = base_url.split("/api")[0]
        invite_link = f"{base_url}/invite/{invite_code.invite.code}"
        return {"invite_link": invite_link}
    else:
        return {"error": "Invite code not found"}, 404


@team_router.post("/api/teams/redeem-invite")
async def redeem_invite(
    code: InviteCode,
    request: Request,
    user: Annotated[User, Depends(validate_user_token)],
):
    invite_code = await dbf.redeem_invite(code, user.username)
    await dbf.query(
        f"with vacations := (SELECT default::Vacation) UPDATE vacations SET {{members += (SELECT default::User filter .username = '{user.username}')}}"
    )
    await dbf.query(
        f"with vacations := (SELECT default::Discussion) UPDATE vacations SET {{members += (SELECT default::User filter .username = '{user.username}')}}"
    )


@team_router.post("/api/teams/delete")
async def delete_teams(
    team: BaseTeam,
    user: Annotated[User, Depends(validate_user_token)],
):
    await dbf.delete_team(team.team_id)
