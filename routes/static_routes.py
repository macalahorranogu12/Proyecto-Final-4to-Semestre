import os

from fastapi import (
    APIRouter,
    HTTPException
)

from fastapi.responses import (
    FileResponse
)

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.get("/")
@router.get("/index.html")
def read_index():
    return FileResponse(
        "index.html"
    )


@router.get("/login.html")
def read_login_page():
    return FileResponse(
        "login.html"
    )


@router.get("/register.html")
def read_register_page():
    return FileResponse(
        "register.html"
    )


@router.get("/usuario.html")
def read_usuario_page():
    return FileResponse(
        "usuario.html"
    )


@router.get("/detalle.html")
def read_detalle_page():
    return FileResponse(
        "detalle.html"
    )


@router.get("/uploads/{filename}")
def get_upload(filename: str):

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    if os.path.exists(file_path):
        return FileResponse(
            file_path
        )

    raise HTTPException(
        status_code=404,
        detail="Imagen no encontrada"
    )


@router.get("/{filename}")
def get_static_asset(
    filename: str
):

    allowed_extensions = (
        ".css",
        ".png",
        ".jpg",
        ".jpeg",
        ".js",
        ".ico"
    )

    if any(
        filename.endswith(ext)
        for ext in allowed_extensions
    ):

        if os.path.exists(filename):
            return FileResponse(
                filename
            )

    raise HTTPException(
        status_code=404,
        detail="Archivo no encontrado"
    )