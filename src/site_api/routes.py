from fastapi import APIRouter, Request

from site_api.edgedb import DatabaseFunctions as dbf

router = APIRouter()


@router.get("/")
async def root():
    ...


@router.post("/query")
async def query_object(request: Request):
    query = await request.json()
    await dbf.query(query)
    # TODO: actual functionality, this is just skeleton code


@router.post("/insert")
async def insert_object():
    ...
