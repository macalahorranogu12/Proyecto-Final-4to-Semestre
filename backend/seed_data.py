"""
seed_data.py - Crea 5 usuarios de prueba con una publicacion cada uno.
Ejecutar con: python seed_data.py
(El servidor debe estar corriendo en http://127.0.0.1:8000)
"""

import io
import sys
import requests

# Forzar UTF-8 en la salida de la consola de Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = "http://127.0.0.1:8000"

# ── Datos de los 5 usuarios ───────────────────────────────────────────────────
USUARIOS = [
    {
        "username": "luna_creativa",
        "email": "luna@example.com",
        "password": "Luna2024!",
        "post": {
            "title": "Atardecer en la montaña",
            "category": "Naturaleza",
            "description": "Capturé este atardecer increíble desde la cima. Los colores eran irrepetibles.",
            "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=1000&fit=crop",
        },
    },
    {
        "username": "pixel_master",
        "email": "pixel@example.com",
        "password": "Pixel2024!",
        "post": {
            "title": "Circuito de neón",
            "category": "Tecnología",
            "description": "Diseño de interfaz futurista con luces de neón en tonos violeta y azul.",
            "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&h=900&fit=crop",
        },
    },
    {
        "username": "chef_artesano",
        "email": "chef@example.com",
        "password": "Chef2024!",
        "post": {
            "title": "Desayuno gourmet",
            "category": "Comida",
            "description": "Un desayuno saludable y delicioso para empezar el día con energía.",
            "image_url": "https://images.unsplash.com/photo-1484723091791-c0e7e53f3ea8?w=800&h=900&fit=crop",
        },
    },
    {
        "username": "wanderlust_k",
        "email": "wanderlust@example.com",
        "password": "Travel2024!",
        "post": {
            "title": "Calles de Tokio",
            "category": "Viajes",
            "description": "La energía de Tokio de noche es algo que no se puede describir con palabras.",
            "image_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&h=1100&fit=crop",
        },
    },
    {
        "username": "arte_vivo",
        "email": "artevivo@example.com",
        "password": "Arte2024!",
        "post": {
            "title": "Pintura abstracta",
            "category": "Arte",
            "description": "Experimentando con colores complementarios y formas libres en acrílico.",
            "image_url": "https://images.unsplash.com/photo-1549490349-8643362247b5?w=800&h=1000&fit=crop",
        },
    },
]


def descargar_imagen(url: str, nombre: str) -> tuple[bytes, str]:
    """Descarga una imagen y devuelve sus bytes y filename."""
    print(f"  [->] Descargando imagen desde Unsplash...")
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    ext = ".jpg"
    return r.content, f"{nombre}{ext}"


def registrar_usuario(datos: dict) -> bool:
    payload = {
        "username": datos["username"],
        "email": datos["email"],
        "password": datos["password"],
    }
    r = requests.post(f"{BASE}/register", json=payload)
    if r.status_code == 200:
        print(f"  [OK] Usuario '{datos['username']}' registrado.")
        return True
    elif r.status_code == 400:
        print(f"  [!]  Usuario '{datos['username']}' ya existe - se saltara el registro.")
        return True  # Continuar con la publicación
    else:
        print(f"  [X] Error al registrar '{datos['username']}': {r.text}")
        return False


def crear_publicacion(username: str, post: dict) -> bool:
    img_bytes, img_filename = descargar_imagen(post["image_url"], username)

    files = {"file": (img_filename, io.BytesIO(img_bytes), "image/jpeg")}
    data = {
        "username": username,
        "title": post["title"],
        "category": post["category"],
        "description": post["description"],
    }

    r = requests.post(f"{BASE}/upload-post", data=data, files=files)
    if r.status_code == 200:
        print(f"  [IMG] Publicacion '{post['title']}' creada exitosamente.")
        return True
    else:
        print(f"  [X] Error al publicar: {r.text}")
        return False


def main():
    print("=" * 55)
    print("  Sembrando datos de prueba en Piterest proyecto")
    print("=" * 55)

    exitosos = 0
    for i, usuario in enumerate(USUARIOS, 1):
        print(f"\n[{i}/5] Procesando @{usuario['username']}...")
        if registrar_usuario(usuario):
            if crear_publicacion(usuario["username"], usuario["post"]):
                exitosos += 1

    print("\n" + "=" * 55)
    print(f"  Proceso completado: {exitosos}/5 usuarios con publicacion.")
    print(f"  Revisa la galeria en http://127.0.0.1:8000")
    print("=" * 55)


if __name__ == "__main__":
    main()
