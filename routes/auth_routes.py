from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from models import (
    engine,
    User,
    UserProfile
)

from schemas import (
    UserRegister,
    UserLogin
)

from security import (
    hash_password,
    verify_password,
    encrypt_data,
    decrypt_data
)

router = APIRouter()


@router.post("/register")
def register(user: UserRegister):

    with Session(engine) as session:

        users = session.exec(
            select(User)
        ).all()

        for db_user in users:

            try:
                db_username = decrypt_data(
                    db_user.username
                )

                db_email = decrypt_data(
                    db_user.email
                ) if db_user.email else None

            except Exception:
                continue

            if db_username == user.username:
                raise HTTPException(
                    status_code=400,
                    detail="Usuario ya registrado"
                )

            if db_email == user.email:
                raise HTTPException(
                    status_code=400,
                    detail="Correo ya registrado"
                )

        new_user = User(
            username=encrypt_data(
                user.username
            ),
            email=encrypt_data(
                user.email
            ),
            hashed_password=hash_password(
                user.password
            )
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        profile = UserProfile(
            user_id=new_user.id
        )

        session.add(profile)
        session.commit()

        return {
            "message":
            "Usuario registrado correctamente"
        }


@router.post("/login")
def login(user: UserLogin):

    with Session(engine) as session:

        users = session.exec(
            select(User)
        ).all()

        found_user = None

        for db_user in users:

            try:
                username = decrypt_data(
                    db_user.username
                )

                email = decrypt_data(
                    db_user.email
                ) if db_user.email else None

            except Exception:
                continue

            if (
                username == user.username
                or
                email == user.username
            ):
                found_user = db_user
                break

        if not found_user:
            raise HTTPException(
                status_code=401,
                detail="Credenciales incorrectas"
            )

        if not verify_password(
            user.password,
            found_user.hashed_password
        ):
            raise HTTPException(
                status_code=401,
                detail="Credenciales incorrectas"
            )

        return {
            "message": "Login exitoso",
            "username": decrypt_data(
                found_user.username
            )
        }