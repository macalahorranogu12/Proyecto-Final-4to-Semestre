import os
import shutil
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from models import (
    engine,
    User,
    UserProfile,
    Post,
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

# Configuración de CORS para permitir solicitudes locales
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_and_tables()

# Carpeta donde se guardan las imágenes subidas
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _validate_image(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imágenes (jpg, jpeg, png, gif, webp)"
        )
    return ext


def _get_user_by_username(session: Session, username: str) -> User:
    """Busca un User descifrando su username. Devuelve el objeto User o lanza 404."""
    users = session.exec(select(User)).all()
    for db_user in users:
        try:
            decrypted = decrypt_data(db_user.username)
        except Exception:
            continue
        if decrypted == username:
            return db_user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# ─── Auth ───────────────────────────────────────────────────────────────────

@app.post("/register")
def register(user: UserRegister):
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        for db_user in users:
            try:
                db_username = decrypt_data(db_user.username)
                db_email = decrypt_data(db_user.email) if db_user.email else None
            except Exception:
                continue

            if db_username == user.username:
                raise HTTPException(
                    status_code=400,
                    detail="El nombre de usuario ya está registrado"
                )
            if db_email and db_email == user.email:
                raise HTTPException(
                    status_code=400,
                    detail="El correo electrónico ya está registrado"
                )

        encrypted_username = encrypt_data(user.username)
        encrypted_email = encrypt_data(user.email)

        new_user = User(
            username=encrypted_username,
            email=encrypted_email,
            hashed_password=hash_password(user.password)
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Crear perfil vacío para el nuevo usuario
        profile = UserProfile(user_id=new_user.id)
        session.add(profile)
        session.commit()

        return {"message": "Usuario registrado correctamente"}


@app.post("/login")
def login(user: UserLogin):
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        found_user = None

        for db_user in users:
            try:
                username = decrypt_data(db_user.username)
                email = decrypt_data(db_user.email) if db_user.email else None
            except Exception:
                continue

            if username == user.username or (email and email == user.username):
                found_user = db_user
                break

        if not found_user:
            raise HTTPException(
                status_code=401,
                detail="Usuario o contraseña incorrectos"
            )

        if not verify_password(user.password, found_user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Usuario o contraseña incorrectos"
            )

        actual_username = decrypt_data(found_user.username)
        return {"message": "Login exitoso", "username": actual_username}


# ─── Perfil ─────────────────────────────────────────────────────────────────

@app.get("/profile/{username}")
def get_profile(username: str):
    """Devuelve avatar_path y bio del usuario."""
    with Session(engine) as session:
        user = _get_user_by_username(session, username)
        profile = session.exec(
            select(UserProfile).where(UserProfile.user_id == user.id)
        ).first()

        if not profile:
            # Crear perfil si no existe (usuarios registrados antes de esta versión)
            profile = UserProfile(user_id=user.id)
            session.add(profile)
            session.commit()
            session.refresh(profile)

        return {
            "username": username,
            "avatar_url": f"/uploads/{os.path.basename(profile.avatar_path)}" if profile.avatar_path else None,
            "bio": profile.bio
        }


@app.post("/upload-avatar")
async def upload_avatar(
    username: str = Form(...),
    file: UploadFile = File(...)
):
    """Sube/reemplaza la foto de perfil del usuario."""
    _validate_image(file.filename)

    with Session(engine) as session:
        user = _get_user_by_username(session, username)
        profile = session.exec(
            select(UserProfile).where(UserProfile.user_id == user.id)
        ).first()

        if not profile:
            profile = UserProfile(user_id=user.id)
            session.add(profile)

        ext = os.path.splitext(file.filename)[1].lower()
        filename = f"avatar_{user.id}{ext}"
        save_path = os.path.join(UPLOAD_DIR, filename)

        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        profile.avatar_path = save_path
        session.commit()

        return {
            "message": "Avatar actualizado",
            "avatar_url": f"/uploads/{filename}"
        }


# ─── Publicaciones ──────────────────────────────────────────────────────────

@app.post("/upload-post")
async def upload_post(
    username: str = Form(...),
    title: str = Form(...),
    description: str = Form(default=""),
    category: str = Form(default="General"),
    file: UploadFile = File(...)
):
    """Crea una nueva publicación con imagen."""
    _validate_image(file.filename)

    with Session(engine) as session:
        user = _get_user_by_username(session, username)

        ext = os.path.splitext(file.filename)[1].lower()
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        filename = f"post_{user.id}_{timestamp}{ext}"
        save_path = os.path.join(UPLOAD_DIR, filename)

        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        post = Post(
            user_id=user.id,
            username_display=username,
            image_path=save_path,
            title=title,
            description=description,
            category=category
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        return {
            "message": "Publicación creada",
            "post_id": post.id,
            "image_url": f"/uploads/{filename}"
        }


@app.get("/posts")
def get_all_posts():
    """Devuelve todas las publicaciones ordenadas por más reciente."""
    with Session(engine) as session:
        posts = session.exec(
            select(Post).order_by(Post.created_at.desc())
        ).all()

        return [
            {
                "id": p.id,
                "username": p.username_display,
                "image_url": f"/uploads/{os.path.basename(p.image_path)}",
                "title": p.title,
                "description": p.description,
                "category": p.category,
                "created_at": p.created_at.isoformat()
            }
            for p in posts
        ]


@app.get("/posts/user/{username}")
def get_user_posts(username: str):
    """Devuelve las publicaciones de un usuario específico."""
    with Session(engine) as session:
        user = _get_user_by_username(session, username)
        posts = session.exec(
            select(Post)
            .where(Post.user_id == user.id)
            .order_by(Post.created_at.desc())
        ).all()

        return [
            {
                "id": p.id,
                "username": p.username_display,
                "image_url": f"/uploads/{os.path.basename(p.image_path)}",
                "title": p.title,
                "description": p.description,
                "category": p.category,
                "created_at": p.created_at.isoformat()
            }
            for p in posts
        ]


# ─── Archivos estáticos ─────────────────────────────────────────────────────

@app.get("/")
@app.get("/index.html")
def read_index():
    return FileResponse("index.html")


@app.get("/login.html")
def read_login_page():
    return FileResponse("login.html")


@app.get("/register.html")
def read_register_page():
    return FileResponse("register.html")


@app.get("/usuario.html")
def read_usuario_page():
    return FileResponse("usuario.html")


@app.get("/detalle.html")
def read_detalle_page():
    return FileResponse("detalle.html")


@app.get("/uploads/{filename}")
def get_upload(filename: str):
    """Sirve imágenes subidas por los usuarios."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Imagen no encontrada")


@app.get("/{filename}")
def get_static_asset(filename: str):
    """
    Ruta dinámica para servir hojas de estilo e imágenes de forma segura.
    Solo permite extensiones seguras para bloquear acceso a archivos del backend.
    """
    allowed_extensions = (".css", ".png", ".jpg", ".jpeg", ".js", ".ico")
    if any(filename.endswith(ext) for ext in allowed_extensions):
        if os.path.exists(filename):
            return FileResponse(filename)
    raise HTTPException(status_code=404, detail="Archivo no encontrado")