from datetime import datetime, timedelta

import jwt
from fastapi import Depends

from site_api.constants import ALGORITHM, SECRET_KEY
from site_api.routes.common import oauth2_scheme
from site_api.routes.models.Models import User


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def validate_user_token(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")

    return User(username=username)
