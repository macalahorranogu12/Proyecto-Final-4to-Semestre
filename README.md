# Proyecto Final — Integrador Cyber

Aplicación web tipo red social construida con **FastAPI** (backend) y **HTML/CSS/JS** vanilla (frontend).

## Estructura del Proyecto

```
Proyecto_Final/
├── backend/           ← Servidor FastAPI (Python)
│   ├── main.py        ← Punto de entrada
│   ├── models.py      ← Modelos SQLite (SQLModel)
│   ├── schemas.py     ← Esquemas Pydantic
│   ├── security.py    ← Hashing bcrypt + cifrado AES
│   ├── requirements.txt
│   ├── database.db    ← Base de datos SQLite
│   ├── routes/        ← Rutas de la API
│   │   ├── auth_routes.py
│   │   ├── post_routes.py
│   │   ├── profile_routes.py
│   │   └── static_routes.py
│   ├── utils/
│   │   └── helpers.py
│   └── uploads/       ← Imágenes subidas por usuarios
│
└── frontend/          ← Interfaz de usuario
    ├── index.html
    ├── login.html
    ├── register.html
    ├── usuario.html
    ├── detalle.html
    ├── *.css          ← Estilos
    ├── sidebar.js     ← Lógica del cliente
    └── *.png          ← Imágenes estáticas
```

## Cómo ejecutar

### 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Iniciar el servidor

```bash
cd backend
uvicorn main:app --reload
```

El servidor estará disponible en: **http://localhost:8000**

### 3. Abrir la app

Visita `http://localhost:8000` en tu navegador.
