import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from site_api.edgedb import DatabaseFunctions as dbf

user_router = APIRouter()


@user_router.get("/users")
async def get_users():
    return await dbf.query("SELECT default::User{**};")


@user_router.get("/users/{user_id}")
async def get_individual_user(user_id: int):
    user = await dbf.query(
        f"SELECT default::User{{**}} FILTER .user_id = {user_id};", query_single=True
    )

    if isinstance(user, str):
        user = json.loads(user)
        user.pop("password")

    return user


@user_router.post("/users/login")
async def login(request: Request):
    res = await request.json()
    assert res.get("credentials")

    if await dbf.login(res.get("credentials")):
        return JSONResponse({"message": "success"})

    return JSONResponse({"message": "failure"}, 401)


@user_router.post("/users/logout")
async def logout(request: Request):
    res = await request.json()
    assert res.get("user")

    if dbf.logout(res.get("user")):
        return JSONResponse({"message": "success"})

    return JSONResponse({"message": "failure"}, 500)


@user_router.post("/users")
async def make_users(request: Request):
    res = await request.json()
    assert res.get("user")

    return await dbf.insert_user(res.get("user"))
