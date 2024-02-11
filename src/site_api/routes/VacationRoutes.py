import json
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import CreateVacation, User, Vacation
from site_api.routes.utils.LoginUtils import validate_user_token

vacation_router = APIRouter()


@vacation_router.get("/vacations")
async def get_vacations():
    return await dbf.query(
        "SELECT default::Vacation {**, members: {username, first_name, last_name, id}};"
    )


@vacation_router.get("/vacations/{vacation_id}")
async def get_individual_vacation(vacation_id: int):
    vacation = await dbf.query(
        f"SELECT default::Vacation{{**, members: {{first_name, last_name, username, id}}}} FILTER .vacation_id = {vacation_id};",
        query_single=True,
    )

    if isinstance(vacation, str):
        vacation = json.loads(vacation)

    return vacation


@vacation_router.post("/vacations")
async def make_vacations(
    create_vacation: CreateVacation,
    current_user: Annotated[User, Depends(validate_user_token)],
):
    return await dbf.insert_vacation(
        create_vacation.vacation, create_vacation.team, current_user
    )
