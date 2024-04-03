import json
from datetime import timedelta
from typing import Annotated

from fastapi import (APIRouter, Depends, File, Form, HTTPException, UploadFile,
                     status)
from fastapi.responses import JSONResponse

from site_api.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from site_api.edgedb import DatabaseFunctions as dbf
from site_api.routes.models.Models import CreateUser, User, UserLogin
from site_api.routes.utils.LoginUtils import (create_access_token,
                                              validate_user_token)
from site_api.utils import retrieve_pfp, upload_profile_picture

user_router = APIRouter()


@user_router.post("/api/users")
async def make_users(user: CreateUser):
    return await dbf.insert_user(user)


@user_router.get("/api/users/delete")
async def delete_users(user: Annotated[User, Depends(validate_user_token)]):
    return await dbf.delete_user(user.username)


@user_router.post("/api/users/update")
async def upload_pfp(
    user: Annotated[User, Depends(validate_user_token)],
    first_name: str = Form(...),
    last_name: str = Form(...),
    image: UploadFile = File(None),
):
    if image:
        upload_profile_picture(user.username, image)

    try:
        await dbf.update_user(first_name, last_name, user.username)
        return JSONResponse({"content": "Success"})
    except Exception as e:
        return JSONResponse({"content": "Failed"}, status_code=500)


@user_router.get("/api/users/pfp")
async def get_pfp(user: Annotated[User, Depends(validate_user_token)]):
    return retrieve_pfp(user.username)


@user_router.get("/api/users/pfp/{username}")
async def get_user_pfp(username: str, _: Annotated[User, Depends(validate_user_token)]):
    return retrieve_pfp(username)


@user_router.post("/api/login")
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
