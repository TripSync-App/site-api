from fastapi import APIRouter, Request

from site_api.edgedb import DatabaseFunctions as dbf

user_router = APIRouter()


@user_router.get("/users")
async def get_users():
    return await dbf.query("SELECT default::User{**};")


@user_router.post("/users")
async def make_users():
    ...
