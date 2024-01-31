import edgedb

DB_HOST = ""
DB_PORT = 0


async def query(query: str) -> list:
    client = edgedb.create_async_client(host=DB_HOST, port=DB_PORT)
    res = await client.query(query)
    await client.aclose()
    return res
