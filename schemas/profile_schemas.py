from sqlmodel import SQLModel


class FollowAction(SQLModel):

    follower: str

    following: str


class ProfileUpdate(SQLModel):

    new_username: str | None = None

    bio: str | None = None