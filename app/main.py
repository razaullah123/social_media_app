from fastapi import FastAPI

from . import models
from . import database
from .routers import post, user, auth,vote

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
async def root():
    return {"data": "Hello World"}
