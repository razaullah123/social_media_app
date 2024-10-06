from itertools import groupby

from fastapi import status, Depends, HTTPException, APIRouter, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, models
from ..database import get_db
from .. import oauth2
from ..schemas import UserOut

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.PostOut])
def posts(db: Session = Depends(get_db), user: UserOut = Depends(oauth2.get_current_user), limit: int = 10,
          skip: int = 0, search: Optional[str] = ""):
    # cursor.execute(""" SELECT * from posts """)
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).filter(models.Post.title.icontains(search)).limit(limit=limit).offset(skip).all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db),
                 user_id: UserOut = Depends(oauth2.get_current_user)):
    # cursor.execute(f""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id=user_id.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, response: Response, db: Session = Depends(get_db),
             user: UserOut = Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * from posts where id = %s """, (str(id)))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.id == id).first()
    if post:
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found")


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user: UserOut = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM posts where id = %s returning * """, (str(id)))
    # post_deleted = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} does not exists")
    if post.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{id}', response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),
                user: UserOut = Depends(oauth2.get_current_user)):
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id=%s RETURNING * """,
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} does not exists")
    if post.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()
