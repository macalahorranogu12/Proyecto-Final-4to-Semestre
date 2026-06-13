from sqlmodel import SQLModel


class UserRegister(SQLModel):

    username: str

    email: str

    password: str

    birthdate: str | None = None


class UserLogin(SQLModel):

    username: str

    password: str