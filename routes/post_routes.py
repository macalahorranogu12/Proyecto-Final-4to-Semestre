import os
import shutil

from datetime import datetime

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from sqlmodel import (
    Session,
    select,
    func
)

from models import (
    engine,
    Post,
    Comment,
    Like,
    Save
)

from schemas import (
    CommentCreate,
    LikeAction,
    SaveAction
)

from utils.helpers import (
    validate_image,
    get_user_by_username
)

from utils.post_utils import (
    build_post_response,
    build_comment_response
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

    validate_image(
        file.filename
    )

    with Session(engine) as session:

        user = get_user_by_username(
            session,
            username
        )

        ext = os.path.splitext(
            file.filename
        )[1].lower()

        timestamp = int(
            datetime.utcnow()
            .timestamp()
            * 1000
        )

        filename = (
            f"post_{user.id}_{timestamp}{ext}"
        )

        save_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        with open(
            save_path,
            "wb"
        ) as f:

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
            select(Post)
            .order_by(
                Post.created_at.desc()
            )
        ).all()

        result = []

        for p in posts:

            count = session.exec(
                select(
                    func.count(
                        Like.id
                    )
                )
                .where(
                    Like.post_id
                    ==
                    p.id
                )
            ).one()

            result.append(
                build_post_response(
                    p,
                    count
                )
            )

        return result


@router.get("/posts/user/{username}")
def get_user_posts(
    username: str
):

    with Session(engine) as session:

        user = get_user_by_username(
            session,
            username
        )

        posts = session.exec(
            select(Post)
            .where(
                Post.user_id
                ==
                user.id
            )
            .order_by(
                Post.created_at.desc()
            )
        ).all()

        result = []

        for p in posts:

            count = session.exec(
                select(
                    func.count(
                        Like.id
                    )
                )
                .where(
                    Like.post_id
                    ==
                    p.id
                )
            ).one()

            result.append(
                build_post_response(
                    p,
                    count
                )
            )

        return result


@router.get(
    "/posts/{post_id}/comments"
)
def get_comments(
    post_id: int
):

    with Session(engine) as session:

        comments = session.exec(
            select(Comment)
            .where(
                Comment.post_id
                ==
                post_id
            )
            .order_by(
                Comment.created_at.asc()
            )
        ).all()

        return [
            build_comment_response(
                c
            )
            for c in comments
        ]