import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import BaseVacation, CreateVacation, User
from site_api.routes.utils.LoginUtils import validate_user_token
from site_api.utils import retrieve_thumbnail, upload_thumbnail_image

vacation_router = APIRouter()


@vacation_router.get("/api/vacations")
async def get_vacations(current_user: Annotated[User, Depends(validate_user_token)]):
    return await dbf.query(
        """
        SELECT default::Vacation {**, discussions: {**, admin_user := default::Vacation.admin_user.username}, members: {username, first_name, last_name, id}}
        filter <str>$username in .members.username OR .admin_user.username = <str>$username;
        """,
        username=current_user.username,
    )


@vacation_router.get("/api/vacations/{vacation_id}")
async def get_individual_vacation(
    vacation_id: int, _: Annotated[User, Depends(validate_user_token)]
):
    vacation = await dbf.query(
        f"SELECT default::Vacation{{**, discussions: {{*, admin_user := default::Vacation.admin_user.username}}, members: {{first_name, last_name, username, id}}}} FILTER .vacation_id = <int64>{vacation_id};",
        query_single=True,
    )

    print(vacation)
    return vacation


@vacation_router.post("/api/vacations")
async def make_vacations(
    create_vacation: CreateVacation,
    current_user: Annotated[User, Depends(validate_user_token)],
):
    if vacation := await dbf.insert_vacation(create_vacation, current_user):
        return vacation


@vacation_router.post("/api/vacations/upload-thumbnail")
async def upload_thumbnail(
    _: Annotated[User, Depends(validate_user_token)],
    vacation: BaseVacation,
    image: UploadFile = File(...),
):
    upload_thumbnail_image(vacation.vacation_id, image)


@vacation_router.get("/api/vacations/thumbnail/{id}")
async def get_thumbnail(
    vacation: BaseVacation, _: Annotated[User, Depends(validate_user_token)]
):
    return retrieve_thumbnail(vacation.vacation_id)
