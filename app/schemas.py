from pydantic import BaseModel, EmailStr
from datetime import datetime

from typing_extensions import Optional


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class config:
        orm_mode = True


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class confiq:
        orm_mode = True


class CreateUser(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
