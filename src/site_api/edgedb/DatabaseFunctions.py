import edgedb

DB_HOST = "edgedb"
DB_PORT = 5656


def create_client():
    return edgedb.create_async_client(
        host=DB_HOST, port=DB_PORT, tls_security="insecure"
    )


async def query(query: str) -> list:
    client = create_client()
    res = await client.query(query)
    await client.aclose()
    return res


async def insert_user(user: dict):
    client = create_client()
    assert user.get("first_name")
    assert user.get("last_name")

    async for tx in client.transaction():
        async with tx:
            query = f"INSERT default::User {{first_name := <str>$first_name, last_name := <str>$last_name, is_logged_in := false}};"
            return await tx.query_single_json(
                query,
                first_name=user.get("first_name"),
                last_name=user.get("last_name"),
            )


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


async def insert_vacation(discussion: dict):
    client = create_client()
    assert discussion.get("admin_user") and isinstance(
        discussion.get("admin_user"), int
    )
    assert discussion.get("name") and isinstance(discussion.get("name"), str)
    assert discussion.get("discussions") and isinstance(
        discussion.get("discussions"), list
    )
    assert discussion.get("members") and isinstance(discussion.get("members"), list)

    DISCUSSIONS = ""
    MEMBERS = ""

    if discussion.get("discussions"):
        DISCUSSIONS = f"discussions := (SELECT default::Discussion filter .discussion_id = array_unpack(<array<int64>>{discussion.get('discussions')})),"

    if discussion.get("members"):
        MEMBERS = f"members := (SELECT default::User filter .user_id = array_unpack(<array<int64>>{discussion.get('members')})),"

    async for tx in client.transaction():
        async with tx:
            query = f"""
            INSERT default::Vacation {{
            admin_user := (SELECT default::User filter .user_id = <int64>$admin_user),
            name := <str>$name,
            {DISCUSSIONS} {MEMBERS}
            }};"""
            return await tx.query_single_json(
                query,
                admin_user=discussion.get("admin_user"),
                name=discussion.get("name"),
            )
