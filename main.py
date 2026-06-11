from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import create_db_and_tables

from routes.auth_routes import router as auth_router
from routes.profile_routes import router as profile_router
from routes.post_routes import router as post_router
from routes.static_routes import router as static_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_and_tables()

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(post_router)
app.include_router(static_router)