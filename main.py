from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware

from models import (
    engine,
    User,
    UserRegister,
    UserLogin,
    create_db_and_tables
)

from auth import (
    hash_password,
    verify_password,
    encrypt_data,
    decrypt_data
)

app = FastAPI()

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

create_db_and_tables()


@app.post("/register")
def register(user: UserRegister):

    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Las contraseñas no coinciden"
        )

    with Session(engine) as session:

        users = session.exec(select(User)).all()

        for db_user in users:

            try:
                username = decrypt_data(
                    db_user.username
                )

                correo = decrypt_data(
                    db_user.correo
                )

            except:
                continue

            if username.lower() == user.username.lower():
                raise HTTPException(
                    status_code=400,
                    detail="El usuario ya existe"
                )

            if correo.lower() == user.correo.lower():
                raise HTTPException(
                    status_code=400,
                    detail="El correo ya está registrado"
                )

        new_user = User(
            username=encrypt_data(user.username),
            nombre=encrypt_data(user.nombre),
            apellido=encrypt_data(user.apellido),
            sexo=encrypt_data(user.sexo),
            fecha_nacimiento=encrypt_data(
                user.fecha_nacimiento
            ),
            correo=encrypt_data(user.correo),

            hashed_password=hash_password(
                user.password
            )
        )

        session.add(new_user)
        session.commit()

        return {
            "message": "Usuario registrado correctamente"
        }


@app.post("/login")
def login(user: UserLogin):

    with Session(engine) as session:

        users = session.exec(select(User)).all()

        found_user = None

        for db_user in users:

            try:
                correo = decrypt_data(
                    db_user.correo
                )

            except:
                continue

            if correo.lower() == user.correo.lower():

                found_user = db_user
                break

        if not found_user:

            raise HTTPException(
                status_code=401,
                detail="Correo o contraseña incorrectos"
            )

        password_correct = verify_password(
            user.password,
            found_user.hashed_password
        )

        if not password_correct:

            raise HTTPException(
                status_code=401,
                detail="Correo o contraseña incorrectos"
            )

        return {
            "message": "Login exitoso"
        }