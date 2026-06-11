from sqlmodel import SQLModel
from typing import Optional


class UserRegister(SQLModel):
    username: str
    email: str
    password: str
    birthdate: str | None = None  # YYYY-MM-DD


class UserLogin(SQLModel):
    username: str
    password: str


class CommentCreate(SQLModel):
    username: str
    content: str


class LikeAction(SQLModel):
    username: str


class SaveAction(SQLModel):
    username: str


class FollowAction(SQLModel):
    follower: str
    following: str


class ProfileUpdate(SQLModel):
    new_username: str | None = None
    bio: str | None = None