from sqlmodel import SQLModel, Field, create_engine

engine = create_engine("sqlite:///database.db")


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    username: str
    nombre: str
    apellido: str
    sexo: str
    fecha_nacimiento: str
    correo: str

    hashed_password: str


class UserRegister(SQLModel):
    username: str
    nombre: str
    apellido: str
    sexo: str
    fecha_nacimiento: str
    correo: str

    password: str
    confirm_password: str


class UserLogin(SQLModel):
    correo: str
    password: str


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)