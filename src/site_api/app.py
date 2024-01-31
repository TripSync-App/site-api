from fastapi import FastAPI

from site_api.routes import *

app = FastAPI()
app.include_router(user_router)
app.include_router(vacation_router)
app.include_router(discussion_router)
app.include_router(message_router)
