from fastapi import FastAPI

from site_api.routes.UserRoutes import user_router

app = FastAPI()
app.include_router(user_router)
