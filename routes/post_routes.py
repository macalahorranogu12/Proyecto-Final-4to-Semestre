import os
import shutil

from datetime import datetime

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from sqlmodel import (
    Session,
    select
)

from models import (
    engine,
    Post
)

from utils.helpers import (
    validate_image,
    get_user_by_username
)

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.post("/upload-post")
async def upload_post(
    username: str = Form(...),
    title: str = Form(...),
    description: str = Form(default=""),
    category: str = Form(default="General"),
    file: UploadFile = File(...)
):

    validate_image(file.filename)

    with Session(engine) as session:

        user = get_user_by_username(
            session,
            username
        )

        ext = os.path.splitext(
            file.filename
        )[1].lower()

        timestamp = int(
            datetime.utcnow().timestamp()
            * 1000
        )

        filename = (
            f"post_{user.id}_{timestamp}{ext}"
        )

        save_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        with open(save_path, "wb") as f:
            shutil.copyfileobj(
                file.file,
                f
            )

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
            "message":
                "Publicación creada",
            "post_id":
                post.id,
            "image_url":
                f"/uploads/{filename}"
        }


@router.get("/posts")
def get_all_posts():

    with Session(engine) as session:

        posts = session.exec(
            select(Post).order_by(
                Post.created_at.desc()
            )
        ).all()

        return [
            {
                "id": p.id,
                "username":
                    p.username_display,
                "image_url":
                    f"/uploads/{os.path.basename(p.image_path)}",
                "title":
                    p.title,
                "description":
                    p.description,
                "category":
                    p.category,
                "created_at":
                    p.created_at.isoformat()
            }
            for p in posts
        ]


@router.get("/posts/user/{username}")
def get_user_posts(username: str):

    with Session(engine) as session:

        user = get_user_by_username(
            session,
            username
        )

        posts = session.exec(
            select(Post)
            .where(
                Post.user_id == user.id
            )
            .order_by(
                Post.created_at.desc()
            )
        ).all()

        return [
            {
                "id": p.id,
                "username":
                    p.username_display,
                "image_url":
                    f"/uploads/{os.path.basename(p.image_path)}",
                "title":
                    p.title,
                "description":
                    p.description,
                "category":
                    p.category,
                "created_at":
                    p.created_at.isoformat()
            }
            for p in posts
        ]