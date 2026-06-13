from datetime import datetime

from sqlmodel import (
    SQLModel,
    Field
)

from database import (
    engine,
    migrate
)


class User(
    SQLModel,
    table=True
):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    username: str

    email: str | None = Field(
        default=None
    )

    hashed_password: str


class UserProfile(
    SQLModel,
    table=True
):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    user_id: int = Field(
        foreign_key="user.id",
        unique=True
    )

    avatar_path: str | None = Field(
        default=None
    )

    bio: str | None = Field(
        default=None
    )

    is_adult: bool = Field(
        default=False
    )


class Post(
    SQLModel,
    table=True
):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    user_id: int = Field(
        foreign_key="user.id"
    )

    username_display: str

    image_path: str

    title: str

    description: str | None = Field(
        default=None
    )

    category: str | None = Field(
        default=None
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class Comment(
    SQLModel,
    table=True
):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    post_id: int = Field(
        foreign_key="post.id"
    )

    user_id: int = Field(
        foreign_key="user.id"
    )

    username_display: str

    content: str

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class Like(
    SQLModel,
    table=True
):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    post_id: int = Field(
        foreign_key="post.id"
    )

    user_id: int = Field(
        foreign_key="user.id"
    )


class Save(
    SQLModel,
    table=True
):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    post_id: int = Field(
        foreign_key="post.id"
    )

    user_id: int = Field(
        foreign_key="user.id"
    )


class Follow(
    SQLModel,
    table=True
):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    follower_id: int = Field(
        foreign_key="user.id"
    )

    following_id: int = Field(
        foreign_key="user.id"
    )


def create_db_and_tables():

    SQLModel.metadata.create_all(
        engine
    )

    migrate()