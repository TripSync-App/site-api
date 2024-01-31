from fastapi import APIRouter, Request

from site_api.edgedb import DatabaseFunctions as dbf

vacation_router = APIRouter()


@vacation_router.get("/vacations")
async def get_vacations():
    return await dbf.query("SELECT default::Vacation {**};")


@vacation_router.post("/vacations")
async def make_vacations():
    ...
