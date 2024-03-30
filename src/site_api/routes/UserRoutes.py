import json
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from site_api.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import CreateUser, User, UserLogin
from site_api.routes.utils.LoginUtils import (create_access_token,
                                              validate_user_token)
from site_api.utils import retrieve_pfp, upload_profile_picture

user_router = APIRouter()


@user_router.post("/users")
async def make_users(user: CreateUser):
    return await dbf.insert_user(user)


@user_router.post("/users/upload-pfp")
async def upload_pfp(
    user: Annotated[User, Depends(validate_user_token)], image: UploadFile = File(...)
):
    upload_profile_picture(user.username, image)


@user_router.get("/users/pfp")
async def get_pfp(user: Annotated[User, Depends(validate_user_token)]):
    return retrieve_pfp(user.username)


@user_router.get("/users/pfp/{username}")
async def get_user_pfp(username: str, _: Annotated[User, Depends(validate_user_token)]):
    return retrieve_pfp(username)


@user_router.post("/login")
async def login(user_login: UserLogin):
    if user := await dbf.login(user_login):
        expire_time = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"sub": user_login.username}
        token = create_access_token(data, expires_delta=expire_time)
        return {"access_token": token, "token_type": "Bearer", "userData": user[0]}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )


@user_router.post("/logout")
async def logout(user: Annotated[User, Depends(validate_user_token)]):
    if dbf.logout(user):
        return JSONResponse({"message": "success"})

    return JSONResponse({"message": "failure"}, 500)
