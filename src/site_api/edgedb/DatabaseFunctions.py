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
