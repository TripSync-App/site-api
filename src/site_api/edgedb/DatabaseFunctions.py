import logging
from typing import List

import bcrypt
import edgedb
from fastapi import HTTPException, status

from site_api.routes.models.Models import (BaseTeam, BaseUser, CreateUser,
                                           IDUser, InviteCode, Team, User,
                                           UserLogin, Vacation)

LOG = logging.getLogger(__name__)

DB_HOST = "edgedb"
DB_PORT = 5656


def create_client():
    return edgedb.create_async_client(
        dsn="edgedb://edgedb:edgedb@edgedb:5656", tls_security="insecure"
    )


async def query(
    query_statement: str, query_single: bool = False, **kwargs
) -> list | str:
    client = create_client()

    query = client.query

    if query_single:
        query = client.query_single

    res = await query(query_statement, **kwargs)
    await client.aclose()
    return res


async def insert_user(user: CreateUser):
    client = create_client()

    _bytes = user.password.encode("utf-8")
    salt = bcrypt.gensalt()

    hash = bcrypt.hashpw(_bytes, salt)

    try:
        async for tx in client.transaction():
            async with tx:
                query = f"INSERT default::User {{username := <str>$username, password := <bytes>$password, first_name := <str>$first_name, last_name := <str>$last_name, is_logged_in := false}};"
                return await tx.query_single_json(
                    query,
                    username=user.username,
                    password=hash,
                    first_name=user.first_name,
                    last_name=user.last_name,
                )

        await client.aclose()
    except edgedb.ConstraintViolationError:
        raise HTTPException(403, "Username taken.")


async def insert_message(message: dict):
    client = create_client()
    assert message.get("author") and isinstance(message.get("author"), int)
    assert message.get("text") and isinstance(message.get("text"), str)

    async for tx in client.transaction():
        async with tx:
            query = f"INSERT default::Message {{text := <str>$text, author := (SELECT default::User filter .user_id = <int64>$author), discussion := (SELECT Discussion filter .discussion_id = <int64>$discussion)}};"
            return await tx.query_single_json(
                query,
                author=message.get("author"),
                text=message.get("text"),
                discussion=message.get("discussion"),
            )

    await client.aclose()


async def insert_discussion(discussion):
    client = create_client()
    async for tx in client.transaction():
        async with tx:
            query = f"INSERT default::Discussion {{title := <str>$title, members := (SELECT default::User filter .user_id in array_unpack(<array<int64>>$members)), vacation := (SELECT default::Vacation filter .vacation_id = <int64>$vacation)}};"
            print(query)
            return await tx.query_single_json(
                query,
                title=discussion.title,
                members=discussion.members,
                vacation=discussion.vacation,
            )

    await client.aclose()


async def insert_vacation(create_vacation, current_user: User):
    client = create_client()
    try:
        async for tx in client.transaction():
            async with tx:
                query = """
                with
                team := (SELECT default::Team filter .team_id = <int64>$team_id),
                vacation := (
                    INSERT default::Vacation {
                        admin_user := (SELECT default::User filter .username = <str>$username),
                        name := <str>$name,
                        members := (SELECT default::User filter .user_id in array_unpack(<array<int64>>$members)),
                        description := <str>$name,
                        color := <str>$color,
                    }
                )
                UPDATE team SET {
                    vacations += vacation
                };
                SELECT default::Vacation {vacation_id, name}
                filter .name = <str>$name and
                .admin_user = (SELECT default::User filter .username = <str>$username);
                """
                await client.aclose()
                return await tx.query_single_json(
                    query,
                    team_id=create_vacation.team,
                    username=current_user.username,
                    name=create_vacation.vacation,
                    members=create_vacation.members,
                    description=create_vacation.description,
                    color=create_vacation.color,
                )
    except edgedb.ConstraintViolationError:
        raise HTTPException(403, "Can't have two vacations with the same name.")


async def login(user_login: UserLogin):
    client = create_client()

    password_hash = await client.query(
        f"SELECT default::User.password filter User.username = <str>$username",
        username=user_login.username,
    )

    if not password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if bcrypt.checkpw(user_login.password.encode("utf-8"), password_hash[0]):
        user = await client.query(
            f"SELECT default::User {{teams: {{**}}, user_id, username, first_name, last_name}} filter User.username = <str>$username",
            username=user_login.username,
        )

        await client.aclose()
        return user

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
                members := {},
                }) SELECT team {team_id, name};
            """,
            name=team.name,
            username=user.username,
        )
        await client.aclose()

    except Exception as e:
        LOG.error(f"Error: {e}")
        raise HTTPException(403, "Not allowed to create a team with the same name.")

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


async def remove_team_member(team: BaseTeam, user: BaseUser):
    client = create_client()

    _team = await client.query(
        """
        with team := (UPDATE default::Team filter .team_id = <int64>$id SET {
            members -= (SELECT default::User filter .username = <str>$member)
        }) SELECT team {team_id, name, members: {username, user_id}};
        """,
        id=team.team_id,
        member=user.username,
    )

    await client.aclose()

    return _team


async def create_invite(team: BaseTeam, code: str):
    client = create_client()

    _code = await client.query(
        """
        WITH
        code := (
            INSERT default::Invite {
            code := <str>$code,
            }
        )
        UPDATE default::Team
        FILTER .team_id = <int64>$team
        SET { invite := code };
        """,
        team=team.team_id,
        code=code,
    )

    await client.aclose()
    return _code


async def get_invite(team: BaseTeam):
    client = create_client()

    _code = await client.query_single(
        """
        SELECT default::Team {
        invite: {
            code
            }
        }
        FILTER .team_id = <int64>$team;
        """,
        team=team.team_id,
    )

    await client.aclose()
    return _code


async def redeem_invite(code: InviteCode, user):
    client = create_client()

    invite = await client.query_single(
        """
        SELECT default::Invite {
        team: {
            team_id
        }
        }
        FILTER .code = <str>$code;
        """,
        code=code.code,
    )

    team_id = invite.team.team_id

    await client.query(
        """
        with team := (UPDATE default::Team filter .team_id = <int64>$id SET {
            members += (SELECT default::User filter .username = <str>$username)
        }) SELECT team {team_id, name, members: {username, user_id}};
        """,
        id=team_id,
        username=user,
    )

    await client.aclose()


async def update_user(first_name: str, last_name: str, username: str):
    client = create_client()

    await client.query_single(
        """
        UPDATE default::User filter .username = <str>$username
        SET {first_name := <str>$first_name, last_name := <str>$last_name};
        """,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )

    await client.aclose()


async def delete_user(username: str):
    client = create_client()

    delete = await client.query_single(
        """
        DELETE default::User filter .username = <str>$username;
        """,
        username=username,
    )

    await client.aclose()
    return delete


async def delete_team(team_id: int):
    client = create_client()

    delete = await client.query_single(
        """
        DELETE default::Team filter .team_id = <int64>$team_id;
        """,
        team_id=team_id,
    )

    await client.aclose()
    return delete
