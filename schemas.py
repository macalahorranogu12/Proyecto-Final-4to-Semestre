from sqlmodel import SQLModel


class UserRegister(SQLModel):
    username: str
    email: str
    password: str


class UserLogin(SQLModel):
    username: str
    password: str