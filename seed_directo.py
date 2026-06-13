"""
seed_directo.py - Inserta 5 usuarios con publicaciones directamente en la DB.
No requiere que el servidor este corriendo.
Ejecutar con: python seed_directo.py
"""

import io
import os
import sys
import requests
from datetime import datetime
from sqlmodel import Session, select

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Importar modelos y auth del propio proyecto
from models import engine, User, UserProfile, Post, create_db_and_tables
from auth import hash_password, encrypt_data, decrypt_data

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

create_db_and_tables()

# ── Datos de los 5 usuarios ───────────────────────────────────────────────────
USUARIOS = [
    {
        "username": "luna_creativa",
        "email": "luna@example.com",
        "password": "Luna2024!",
        "post": {
            "title": "Atardecer en la montana",
            "category": "Naturaleza",
            "description": "Capture este atardecer increible desde la cima. Los colores eran irrepetibles.",
            "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=800&fit=crop",
        },
    },
    {
        "username": "pixel_master",
        "email": "pixel@example.com",
        "password": "Pixel2024!",
        "post": {
            "title": "Circuito de neon",
            "category": "Tecnologia",
            "description": "Diseno de interfaz futurista con luces de neon en tonos violeta y azul.",
            "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=700&fit=crop",
        },
    },
    {
        "username": "chef_artesano",
        "email": "chef@example.com",
        "password": "Chef2024!",
        "post": {
            "title": "Desayuno gourmet",
            "category": "Comida",
            "description": "Un desayuno saludable y delicioso para empezar el dia con energia.",
            "image_url": "https://images.unsplash.com/photo-1484723091791-c0e7e53f3ea8?w=600&h=700&fit=crop",
        },
    },
    {
        "username": "wanderlust_k",
        "email": "wanderlust@example.com",
        "password": "Travel2024!",
        "post": {
            "title": "Calles de Tokio",
            "category": "Viajes",
            "description": "La energia de Tokio de noche es algo que no se puede describir con palabras.",
            "image_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&h=900&fit=crop",
        },
    },
    {
        "username": "arte_vivo",
        "email": "artevivo@example.com",
        "password": "Arte2024!",
        "post": {
            "title": "Pintura abstracta",
            "category": "Arte",
            "description": "Experimentando con colores complementarios y formas libres en acrilico.",
            "image_url": "https://images.unsplash.com/photo-1549490349-8643362247b5?w=600&h=800&fit=crop",
        },
    },
]


def username_existe(session: Session, username: str) -> bool:
    users = session.exec(select(User)).all()
    for u in users:
        try:
            if decrypt_data(u.username) == username:
                return True
        except Exception:
            continue
    return False


def descargar_imagen(url: str, filename: str) -> str | None:
    print(f"    Descargando imagen...")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=30, headers=headers)
        r.raise_for_status()
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"    Guardada en {path} ({len(r.content)//1024} KB)")
        return path
    except Exception as e:
        print(f"    Error descargando imagen: {e}")
        return None


def main():
    print("=" * 55)
    print("  Sembrando datos de prueba en Piterest proyecto")
    print("=" * 55)

    exitosos = 0

    with Session(engine) as session:
        for i, datos in enumerate(USUARIOS, 1):
            print(f"\n[{i}/5] Procesando @{datos['username']}...")

            # Verificar si ya existe
            if username_existe(session, datos["username"]):
                print(f"    [!] Usuario ya existe, se omite.")
                # Verificar si ya tiene post
                users = session.exec(select(User)).all()
                user_id = None
                for u in users:
                    try:
                        if decrypt_data(u.username) == datos["username"]:
                            user_id = u.id
                            break
                    except Exception:
                        continue
                if user_id:
                    posts_existentes = session.exec(
                        select(Post).where(Post.user_id == user_id)
                    ).all()
                    if posts_existentes:
                        print(f"    [!] Ya tiene publicaciones, se omite.")
                        exitosos += 1
                        continue
            else:
                # Crear usuario
                new_user = User(
                    username=encrypt_data(datos["username"]),
                    email=encrypt_data(datos["email"]),
                    hashed_password=hash_password(datos["password"])
                )
                session.add(new_user)
                session.commit()
                session.refresh(new_user)

                # Crear perfil vacío
                profile = UserProfile(user_id=new_user.id)
                session.add(profile)
                session.commit()

                print(f"    [OK] Usuario registrado (ID: {new_user.id})")
                user_id = new_user.id

            # Descargar y guardar imagen
            post_data = datos["post"]
            timestamp = int(datetime.utcnow().timestamp() * 1000)
            img_filename = f"post_{user_id}_{timestamp}.jpg"
            img_path = descargar_imagen(post_data["image_url"], img_filename)

            if not img_path:
                print(f"    [X] No se pudo descargar la imagen. Omitiendo publicacion.")
                continue

            # Crear post en DB
            post = Post(
                user_id=user_id,
                username_display=datos["username"],
                image_path=img_path,
                title=post_data["title"],
                description=post_data["description"],
                category=post_data["category"],
                created_at=datetime.utcnow()
            )
            session.add(post)
            session.commit()
            print(f"    [IMG] Publicacion '{post_data['title']}' creada.")
            exitosos += 1

    print("\n" + "=" * 55)
    print(f"  Proceso completado: {exitosos}/5 usuarios con publicacion.")
    print(f"  Revisa la galeria en http://127.0.0.1:8000")
    print("=" * 55)


if __name__ == "__main__":
    main()
