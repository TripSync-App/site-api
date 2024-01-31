import edgedb

DB_HOST = "edgedb"
DB_PORT = 5656


async def query(query: str) -> list:
    client = edgedb.create_async_client(
        host=DB_HOST, port=DB_PORT, tls_security="insecure"
    )
    res = await client.query(query)
    await client.aclose()
    return res
