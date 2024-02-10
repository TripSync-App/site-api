from typing import List

from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str


class UserLogin(BaseUser):
    password: str


class IDUser(BaseModel):
    user_id: int


class User(BaseUser):
    ...


class BaseTeam(BaseModel):
    team_id: int


class Team(BaseModel):
    name: str


class AddTeamMembers(BaseModel):
    team: BaseTeam
    data: List[IDUser]
