from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine

engine = create_engine("sqlite:///database.db")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str | None = Field(default=None)
    hashed_password: str


class UserProfile(SQLModel, table=True):
    """Perfil extendido del usuario: foto de perfil y bio."""
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    avatar_path: str | None = Field(default=None)
    bio: str | None = Field(default=None)


class Post(SQLModel, table=True):
    """Publicación de imagen creada por un usuario."""
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    username_display: str                # Username en texto plano para mostrar rápido
    image_path: str                      # Ruta relativa dentro de uploads/
    title: str
    description: str | None = Field(default=None)
    category: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Schemas de Request/Response ───────────────────────────────────────────

class UserRegister(SQLModel):
    username: str
    email: str
    password: str


class UserLogin(SQLModel):
    username: str
    password: str


# ─── Inicialización ─────────────────────────────────────────────────────────

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)