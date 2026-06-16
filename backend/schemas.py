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


class UploadUrlRequest(SQLModel):
    filename: str
    contentType: str


class UploadUrlResponse(SQLModel):
    url: str
    key: str


class RegisterPostRequest(SQLModel):
    s3_key: str
    title: str
    description: str | None = None
    category: str | None = "General"
    user: str


class RegisterPostResponse(SQLModel):
    post_id: int
    image_url: str