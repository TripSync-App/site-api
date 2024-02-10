import json
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from site_api.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import BaseUser, User, UserLogin
from site_api.routes.utils.LoginUtils import (create_access_token,
                                              validate_user_token)

user_router = APIRouter()


@user_router.post("/users")
async def make_users(request: Request):
    res = await request.json()
    assert res.get("user")

    return await dbf.insert_user(res.get("user"))


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
async def login(user_login: UserLogin):
    if await dbf.login(user_login):
        expire_time = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"sub": user_login.username}
        token = create_access_token(data, expires_delta=expire_time)
        return {"access_token": token, "token_type": "Bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )


@user_router.post("/users/logout")
async def logout(user: Annotated[User, Depends(validate_user_token)]):
    if dbf.logout(user):
        return JSONResponse({"message": "success"})

    return JSONResponse({"message": "failure"}, 500)
