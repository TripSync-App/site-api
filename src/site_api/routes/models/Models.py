from typing import List, Optional

from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str


class UserLogin(BaseUser):
    password: str


class IDUser(BaseModel):
    user_id: int


class User(BaseUser): ...


class CreateUser(BaseUser):
    first_name: str
    last_name: str
    password: str


class BaseTeam(BaseModel):
    team_id: int


class Team(BaseModel):
    name: str


class AddTeamMembers(BaseModel):
    team: BaseTeam
    data: List[IDUser]


class RemoveTeamMember(BaseModel):
    team: BaseTeam


class Vacation(BaseModel):
    name: str


class BaseVacation(BaseModel):
    vacation_id: int


class CreateVacation(BaseModel):
    team: int
    vacation: str
    members: list
    # imageUrl: Optional[str]
    # description: Optional[str]
    # tags: Optional[str]
    # color: Optional[str]


class InviteCode(BaseModel):
    code: str


class Discussion(BaseModel):
    discussion_id: int


class CreateDiscussion(BaseModel):
    title: str
    members: list
    vacation: int


class FinalizeDiscussion(BaseModel):
    discussion: int
    is_finalized: bool
