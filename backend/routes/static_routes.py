import os

from fastapi import (
    APIRouter,
    HTTPException
)

from fastapi.responses import (
    FileResponse
)

router = APIRouter()

# Directorio raíz del backend (donde vive este archivo al ejecutarse con uvicorn)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BACKEND_DIR, "..", "frontend")
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")


def _frontend(filename: str) -> str:
    """Devuelve la ruta absoluta a un archivo del frontend."""
    return os.path.normpath(os.path.join(FRONTEND_DIR, filename))


@router.get("/")
@router.get("/index.html")
def read_index():
    return FileResponse(_frontend("index.html"))


@router.get("/login.html")
def read_login_page():
    return FileResponse(_frontend("login.html"))


@router.get("/register.html")
def read_register_page():
    return FileResponse(_frontend("register.html"))


@router.get("/usuario.html")
def read_usuario_page():
    return FileResponse(_frontend("usuario.html"))


@router.get("/detalle.html")
def read_detalle_page():
    return FileResponse(_frontend("detalle.html"))


@router.get("/uploads/{filename}")
def get_upload(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(file_path):
        return FileResponse(file_path)

    raise HTTPException(
        status_code=404,
        detail="Imagen no encontrada"
    )


@router.get("/{filename}")
def get_static_asset(filename: str):
    allowed_extensions = (
        ".css",
        ".png",
        ".jpg",
        ".jpeg",
        ".js",
        ".ico"
    )

    if any(filename.endswith(ext) for ext in allowed_extensions):
        path = _frontend(filename)
        if os.path.exists(path):
            return FileResponse(path)

    raise HTTPException(
        status_code=404,
        detail="Archivo no encontrado"
    )