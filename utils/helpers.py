import os

from fastapi import HTTPException
from sqlmodel import Session, select

from models import User
from security import decrypt_data

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp"
}


def validate_image(filename: str):
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imágenes"
        )

    return ext


def get_user_by_username(
    session: Session,
    username: str
):
    users = session.exec(select(User)).all()

    for db_user in users:
        try:
            decrypted = decrypt_data(
                db_user.username
            )
        except Exception:
            continue

        if decrypted == username:
            return db_user

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )