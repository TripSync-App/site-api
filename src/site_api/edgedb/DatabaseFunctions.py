from typing import List

import bcrypt
import edgedb
from fastapi import HTTPException

from site_api.routes.models.Models import (BaseTeam, BaseUser, IDUser, Team,
                                           User, UserLogin, Vacation)

DB_HOST = "edgedb"
DB_PORT = 5656


def create_client():
    return edgedb.create_async_client(
        host=DB_HOST, port=DB_PORT, tls_security="insecure"
    )


async def query(query_statement: str, query_single: bool = False) -> list | str:
    client = create_client()

    query = client.query

    if query_single:
        query = client.query_single_json

    res = await query(query_statement)
    await client.aclose()
    return res


async def insert_user(user: dict):
    client = create_client()
    assert user.get("first_name")
    assert user.get("last_name")
    assert user.get("username")
    assert user.get("password")

    _bytes = user["password"].encode("utf-8")
    salt = bcrypt.gensalt()

    hash = bcrypt.hashpw(_bytes, salt)

    async for tx in client.transaction():
        async with tx:
            query = f"INSERT default::User {{username := <str>$username, password := <bytes>$password, first_name := <str>$first_name, last_name := <str>$last_name, is_logged_in := false}};"
            return await tx.query_single_json(
                query,
                username=user.get("username"),
                password=hash,
                first_name=user.get("first_name"),
                last_name=user.get("last_name"),
            )

    await client.aclose()


async def insert_message(message: dict):
    client = create_client()
    assert message.get("author") and isinstance(message.get("author"), int)
    assert message.get("text") and isinstance(message.get("text"), str)

    async for tx in client.transaction():
        async with tx:
            query = f"INSERT default::Message {{text := <str>$text, author := (SELECT default::User filter .user_id = <int64>$author)}};"
            return await tx.query_single_json(
                query,
                author=message.get("author"),
                text=message.get("text"),
            )

    await client.aclose()


async def insert_discussion(discussion: dict):
    client = create_client()
    assert discussion.get("title") and isinstance(discussion.get("title"), str)
    assert discussion.get("members") and isinstance(
        discussion.get("members"), list
    )  # NOTE: list[int]
    assert discussion.get("vacation") and isinstance(discussion.get("vacation"), int)

    async for tx in client.transaction():
        async with tx:
            query = f"INSERT default::Discussion {{title := <str>$title, members := (SELECT default::User filter .user_id in array_unpack(<array<int64>>$members)), vacation := (SELECT default::Vacation filter .vacation_id = <int64>$vacation)}};"
            return await tx.query_single_json(
                query,
                title=discussion.get("title"),
                members=discussion.get("members"),
                vacation=discussion.get("vacation"),
            )

    await client.aclose()


async def insert_vacation(vacation: Vacation, team: BaseTeam, current_user: User):
    client = create_client()
    async for tx in client.transaction():
        async with tx:
            query = """
            with
            team := (SELECT default::Team filter .team_id = <int64>$team_id),
            vacation := (
                INSERT default::Vacation {
                    admin_user := (SELECT default::User filter .username = <str>$username),
                    name := <str>$name,
                }
            )
            UPDATE team SET {
                vacations += vacation
            };
            SELECT vacation {vacation_id, name};
            """
            return await tx.query_single_json(
                query,
                team_id=team.team_id,
                username=current_user.username,
                name=vacation.name,
            )

    await client.aclose()


async def login(user_login: UserLogin):
    client = create_client()

    password_hash = await client.query(
        f"SELECT default::User.password filter User.username = <str>$username",
        username=user_login.username,
    )

    if bcrypt.checkpw(user_login.password.encode("utf-8"), password_hash[0]):
        await client.query(
            f"UPDATE default::User filter User.username = <str>$username SET {{is_logged_in := true}}",
            username=user_login.username,
        )

        await client.aclose()
        return True

    await client.aclose()
    return False


async def logout(user: BaseUser):
    client = create_client()

    if client.query(
        "UPDATE default::User filter .username = <str>$username SET {{is_logged_in := false}}",
        username=user.username,
    ):
        return True
    else:
        return False


async def create_team(team: Team, user: User):
    client = create_client()

    try:
        _team = await client.query(
            """
            with team := (INSERT default::Team {
                name := <str>$name,
                admin_user := (SELECT default::User filter .username = <str>$username),
                members := (SELECT default::User filter .username = <str>$username)
                }) SELECT team {team_id, name};
            """,
            name=team.name,
            username=user.username,
        )

    except Exception:
        raise HTTPException(403, "Not allowed to create a team with the same name.")

    await client.aclose()

    return _team


async def add_team_members(team: BaseTeam, users: List[IDUser]):
    client = create_client()

    _team = await client.query(
        """
        with team := (UPDATE default::Team filter .team_id = <int64>$id SET {
            members += (SELECT default::User filter .user_id in array_unpack(<array<int64>>$members))
        }) SELECT team {team_id, name, members: {username, user_id}};
        """,
        id=team.team_id,
        members=[user.user_id for user in users],
    )

    await client.aclose()

    return _team
