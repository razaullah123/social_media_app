from multiprocessing.sharedctypes import synchronized
from sys import audit
from typing import Optional, List

from fastapi import FastAPI, status, Response, HTTPException, Depends

from fastapi.params import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from . import models
from .database import engine
from .routers import  post, user, auth



models.Base.metadata.create_all(bind=engine)



app = FastAPI()





while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Uetmardan1234',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Successfully connected to the database")
        break
    except Exception as e:
        print("Connection failed")
        print(f"Error was {e}")
        time.sleep(2)

my_posts = [{"title": "Title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favourite foods", "content": "I like pizza", "id": 2}]


def find_post(id):
    for post in my_posts:
        if post['id'] == id:
            return post
        else:
            return None


def find_index_post(id):
    for i, post in enumerate(my_posts):
        if post['id'] == id:
            return i


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"data": "Hello World"}


