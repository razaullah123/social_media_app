from fastapi import status, Depends, HTTPException, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, models
from ..database import get_db
from .. import oauth2
from ..schemas import UserOut

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.Post])
def posts(db: Session = Depends(get_db), user: UserOut= Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * from posts """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db),
                 user_id: UserOut = Depends(oauth2.get_current_user)):
    # cursor.execute(f""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response, db: Session = Depends(get_db),
             user: UserOut = Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * from posts where id = %s """, (str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post:
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found")


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user: UserOut = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM posts where id = %s returning * """, (str(id)))
    # post_deleted = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} does not exists")
    post.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/post/{id}', response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),
                user: str = Depends(oauth2.get_current_user)):
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id=%s RETURNING * """,
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} does not exists")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()
