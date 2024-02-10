from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from site_api.routes import *

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(vacation_router)
app.include_router(discussion_router)
app.include_router(message_router)
app.include_router(team_router)
