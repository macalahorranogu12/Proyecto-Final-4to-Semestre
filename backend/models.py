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
    """Perfil extendido del usuario: foto de perfil, bio y datos extra."""
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    avatar_path: str | None = Field(default=None)
    bio: str | None = Field(default=None)
    is_adult: bool = Field(default=False)


class Post(SQLModel, table=True):
    """Publicación de imagen creada por un usuario."""
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    username_display: str
    s3_key: str
    title: str
    description: str | None = Field(default=None)
    category: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Comment(SQLModel, table=True):
    """Comentario persistente en una publicación."""
    id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    user_id: int = Field(foreign_key="user.id")
    username_display: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Like(SQLModel, table=True):
    """Like de un usuario a una publicación."""
    id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    user_id: int = Field(foreign_key="user.id")


class Save(SQLModel, table=True):
    """Publicación guardada por un usuario."""
    id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    user_id: int = Field(foreign_key="user.id")


class Follow(SQLModel, table=True):
    """Relación de seguimiento entre usuarios."""
    id: int | None = Field(default=None, primary_key=True)
    follower_id: int = Field(foreign_key="user.id")
    following_id: int = Field(foreign_key="user.id")


# ─── Inicialización ─────────────────────────────────────────────────────────

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _migrate()


def _migrate():
    """Agrega columnas nuevas a tablas existentes que ya tienen datos."""
    from sqlalchemy import text
    migrations = [
        "ALTER TABLE userprofile ADD COLUMN is_adult INTEGER DEFAULT 0",
        "ALTER TABLE post RENAME COLUMN image_path TO s3_key",
    ]
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception:
                pass  # La columna ya existe → ignorar