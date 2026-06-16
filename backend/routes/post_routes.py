import os
import shutil
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException,Query
from sqlmodel import Session, select, func

from models import engine, Post, Comment, Like, Save
from schemas import CommentCreate, LikeAction, SaveAction, UploadUrlRequest, UploadUrlResponse, RegisterPostRequest, RegisterPostResponse
from utils.helpers import validate_image, get_user_by_username
from utils.s3_utils import (
    generate_presigned_url,
    generate_presigned_get_url,
    delete_s3_file
)

router = APIRouter()
UPLOAD_DIR = "uploads"


# ─── Helper ──────────────────────────────────────────────────────────────────

def _post_dict(p: Post, like_count: int = 0):

    return {
        "id": p.id,
        "username": p.username_display,
        "image_url": generate_presigned_get_url(
            p.s3_key
        ),
        "title": p.title,
        "description": p.description,
        "category": p.category,
        "created_at": p.created_at.isoformat(),
        "like_count": like_count,
    }


# ─── Upload Post ──────────────────────────────────────────────────────────────

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
        user = get_user_by_username(session, username)
        ext = os.path.splitext(file.filename)[1].lower()
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        filename = f"post_{user.id}_{timestamp}{ext}"
        save_path = os.path.join(UPLOAD_DIR, filename)
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        post = Post(
            user_id=user.id,
            username_display=username,
            s3_key=save_path,
            title=title,
            description=description,
            category=category
        )
        session.add(post)
        session.commit()
        session.refresh(post)
        return {"message": "Publicación creada", "post_id": post.id, "image_url": f"/uploads/{filename}"}


# ─── S3 Upload Flow ─────────────────────────────────────────────────────────────

@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(request: UploadUrlRequest):
    """Genera una presigned URL para subir un archivo a S3."""
    validate_image(request.filename)
    result = generate_presigned_url(request.filename, request.contentType)
    return result


@router.post("/register-post", response_model=RegisterPostResponse)
async def register_post(request: RegisterPostRequest):
    """Registra un post después de que el archivo fue subido a S3."""
    with Session(engine) as session:
        user = get_user_by_username(session, request.user)
        post = Post(
            user_id=user.id,
            username_display=request.user,
            s3_key=request.s3_key,
            title=request.title,
            description=request.description,
            category=request.category
        )
        session.add(post)
        session.commit()
        session.refresh(post)
        image_url = generate_presigned_get_url(post.s3_key)
        return {
            "post_id": post.id,
            "image_url": image_url
        }


# ─── Get Posts ────────────────────────────────────────────────────────────────

@router.get("/posts")
def get_all_posts():
    with Session(engine) as session:
        posts = session.exec(select(Post).order_by(Post.created_at.desc())).all()
        result = []
        for p in posts:
            count = session.exec(
                select(func.count(Like.id)).where(Like.post_id == p.id)
            ).one()
            result.append(_post_dict(p, count))
        return result


@router.get("/posts/user/{username}")
def get_user_posts(username: str):
    with Session(engine) as session:
        user = get_user_by_username(session, username)
        posts = session.exec(
            select(Post).where(Post.user_id == user.id).order_by(Post.created_at.desc())
        ).all()
        result = []
        for p in posts:
            count = session.exec(
                select(func.count(Like.id)).where(Like.post_id == p.id)
            ).one()
            result.append(_post_dict(p, count))
        return result


# ─── Comments ─────────────────────────────────────────────────────────────────

@router.get("/posts/{post_id}/comments")
def get_comments(post_id: int):
    with Session(engine) as session:
        comments = session.exec(
            select(Comment)
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
        ).all()
        return [
            {
                "id": c.id,
                "username": c.username_display,
                "content": c.content,
                "created_at": c.created_at.isoformat()
            }
            for c in comments
        ]


@router.post("/posts/{post_id}/comments")
def add_comment(post_id: int, data: CommentCreate):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Publicación no encontrada")
        user = get_user_by_username(session, data.username)
        comment = Comment(
            post_id=post_id,
            user_id=user.id,
            username_display=data.username,
            content=data.content
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)
        return {
            "id": comment.id,
            "username": comment.username_display,
            "content": comment.content,
            "created_at": comment.created_at.isoformat()
        }


# ─── Likes ────────────────────────────────────────────────────────────────────

@router.get("/posts/{post_id}/likes")
def get_likes(post_id: int, username: str = None):
    with Session(engine) as session:
        count = session.exec(
            select(func.count(Like.id)).where(Like.post_id == post_id)
        ).one()
        liked = False
        if username:
            try:
                user = get_user_by_username(session, username)
                existing = session.exec(
                    select(Like).where(Like.post_id == post_id, Like.user_id == user.id)
                ).first()
                liked = existing is not None
            except Exception:
                pass
        return {"count": count, "liked": liked}


@router.post("/posts/{post_id}/like")
def like_post(post_id: int, data: LikeAction):
    with Session(engine) as session:
        user = get_user_by_username(session, data.username)
        existing = session.exec(
            select(Like).where(Like.post_id == post_id, Like.user_id == user.id)
        ).first()
        if not existing:
            session.add(Like(post_id=post_id, user_id=user.id))
            session.commit()
        count = session.exec(
            select(func.count(Like.id)).where(Like.post_id == post_id)
        ).one()
        return {"liked": True, "count": count}


@router.delete("/posts/{post_id}/like")
def unlike_post(post_id: int, username: str):
    with Session(engine) as session:
        user = get_user_by_username(session, username)
        existing = session.exec(
            select(Like).where(Like.post_id == post_id, Like.user_id == user.id)
        ).first()
        if existing:
            session.delete(existing)
            session.commit()
        count = session.exec(
            select(func.count(Like.id)).where(Like.post_id == post_id)
        ).one()
        return {"liked": False, "count": count}


# ─── Saves ────────────────────────────────────────────────────────────────────

@router.get("/posts/{post_id}/saved")
def get_saved(post_id: int, username: str = None):
    with Session(engine) as session:
        saved = False
        if username:
            try:
                user = get_user_by_username(session, username)
                existing = session.exec(
                    select(Save).where(Save.post_id == post_id, Save.user_id == user.id)
                ).first()
                saved = existing is not None
            except Exception:
                pass
        return {"saved": saved}


@router.post("/posts/{post_id}/save")
def save_post(post_id: int, data: SaveAction):
    with Session(engine) as session:
        user = get_user_by_username(session, data.username)
        existing = session.exec(
            select(Save).where(Save.post_id == post_id, Save.user_id == user.id)
        ).first()
        if not existing:
            session.add(Save(post_id=post_id, user_id=user.id))
            session.commit()
        return {"saved": True}


@router.delete("/posts/{post_id}/save")
def unsave_post(post_id: int, username: str):
    with Session(engine) as session:
        user = get_user_by_username(session, username)
        existing = session.exec(
            select(Save).where(Save.post_id == post_id, Save.user_id == user.id)
        ).first()
        if existing:
            session.delete(existing)
            session.commit()
        return {"saved": False}
    
# ─── Delete Post ───────────────────────────────────────────────

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, username: str = Query(...)):

    with Session(engine) as session:

        post = session.get(Post, post_id)

        if not post:
            raise HTTPException(
                status_code=404,
                detail="Publicación no encontrada"
            )

        user = get_user_by_username(session, username)

        if post.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="No puedes eliminar esta publicación"
            )

        try:

            # ─── borrar imagen en S3/local ───
            if post.s3_key:
                delete_s3_file(post.s3_key)

            # ─── borrar comentarios ───
            comments = session.exec(
                select(Comment).where(Comment.post_id == post_id)
            ).all()

            for c in comments:
                session.delete(c)

            # ─── borrar likes ───
            likes = session.exec(
                select(Like).where(Like.post_id == post_id)
            ).all()

            for l in likes:
                session.delete(l)

            # ─── borrar saves ───
            saves = session.exec(
                select(Save).where(Save.post_id == post_id)
            ).all()

            for s in saves:
                session.delete(s)

            # ─── borrar post ───
            session.delete(post)
            session.commit()

            return {
                "success": True,
                "message": "Publicación eliminada"
            }

        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )