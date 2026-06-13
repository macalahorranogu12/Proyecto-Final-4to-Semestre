from sqlmodel import SQLModel


class CommentCreate(SQLModel):

    username: str

    content: str


class LikeAction(SQLModel):

    username: str


class SaveAction(SQLModel):

    username: str