import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlmodel import Session, select

from models import engine, User, UserProfile, Post, Comment, Like, Save, Follow
from schemas import ProfileUpdate, FollowAction
from utils.helpers import validate_image, get_user_by_username
from security import encrypt_data, decrypt_data
from utils.s3_utils import generate_presigned_get_url

router = APIRouter()
UPLOAD_DIR = "uploads"


from utils.s3_utils import generate_presigned_get_url


def _post_dict(p):

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
        "like_count": 0,
    }


# ─── Perfil ───────────────────────────────────────────────────────────────────

@router.get("/profile/{username}")
def get_profile(username: str):
    with Session(engine) as session:
        user = get_user_by_username(session, username)
        profile = session.exec(
            select(UserProfile).where(UserProfile.user_id == user.id)
        ).first()
        if not profile:
            profile = UserProfile(user_id=user.id)
            session.add(profile)
            session.commit()
            session.refresh(profile)

        followers_count = len(session.exec(
            select(Follow).where(Follow.following_id == user.id)
        ).all())
        following_count = len(session.exec(
            select(Follow).where(Follow.follower_id == user.id)
        ).all())

        return {
            "username": username,
            "avatar_url": f"/uploads/{os.path.basename(profile.avatar_path)}" if profile.avatar_path else None,
            "bio": profile.bio,
            "is_adult": bool(profile.is_adult),
            "followers_count": followers_count,
            "following_count": following_count
        }


@router.put("/profile/{username}")
def update_profile(username: str, data: ProfileUpdate):
    with Session(engine) as session:
        user = get_user_by_username(session, username)
        profile = session.exec(
            select(UserProfile).where(UserProfile.user_id == user.id)
        ).first()
        if not profile:
            profile = UserProfile(user_id=user.id)
            session.add(profile)

        # Actualizar bio
        if data.bio is not None:
            profile.bio = data.bio

        new_name = username
        # Actualizar username
        if data.new_username and data.new_username.strip() and data.new_username.strip() != username:
            new_name = data.new_username.strip()
            # Verificar disponibilidad
            all_users = session.exec(select(User)).all()
            for u in all_users:
                if u.id == user.id:
                    continue
                try:
                    dec = decrypt_data(u.username)
                    if dec == new_name:
                        raise HTTPException(status_code=400, detail="Nombre de usuario ya en uso")
                except HTTPException:
                    raise
                except Exception:
                    pass

            user.username = encrypt_data(new_name)

            # Actualizar username_display en posts y comentarios
            for p in session.exec(select(Post).where(Post.user_id == user.id)).all():
                p.username_display = new_name
            for c in session.exec(select(Comment).where(Comment.user_id == user.id)).all():
                c.username_display = new_name

        session.commit()
        return {"message": "Perfil actualizado", "username": new_name}


@router.post("/upload-avatar")
async def upload_avatar(username: str = Form(...), file: UploadFile = File(...)):
    validate_image(file.filename)
    with Session(engine) as session:
        user = get_user_by_username(session, username)
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
        return {"message": "Avatar actualizado", "avatar_url": f"/uploads/{filename}"}


# ─── Posts liked / saved ──────────────────────────────────────────────────────

@router.get("/profile/{username}/liked-posts")
def get_liked_posts(username: str):
    with Session(engine) as session:
        user = get_user_by_username(session, username)
        likes = session.exec(select(Like).where(Like.user_id == user.id)).all()
        result = []
        for lk in likes:
            p = session.get(Post, lk.post_id)
            if p:
                result.append(_post_dict(p))
        return result


@router.get("/profile/{username}/saved-posts")
def get_saved_posts(username: str):
    with Session(engine) as session:
        user = get_user_by_username(session, username)
        saves = session.exec(select(Save).where(Save.user_id == user.id)).all()
        result = []
        for sv in saves:
            p = session.get(Post, sv.post_id)
            if p:
                result.append(_post_dict(p))
        return result


# ─── Seguidores / Seguidos ────────────────────────────────────────────────────

@router.post("/follow")
def follow_user(data: FollowAction):
    with Session(engine) as session:
        follower = get_user_by_username(session, data.follower)
        following = get_user_by_username(session, data.following)
        if follower.id == following.id:
            raise HTTPException(status_code=400, detail="No puedes seguirte a ti mismo")
        existing = session.exec(
            select(Follow).where(
                Follow.follower_id == follower.id,
                Follow.following_id == following.id
            )
        ).first()
        if not existing:
            session.add(Follow(follower_id=follower.id, following_id=following.id))
            session.commit()
        return {"following": True}


@router.delete("/follow")
def unfollow_user(follower: str, following: str):
    with Session(engine) as session:
        follower_user = get_user_by_username(session, follower)
        following_user = get_user_by_username(session, following)
        existing = session.exec(
            select(Follow).where(
                Follow.follower_id == follower_user.id,
                Follow.following_id == following_user.id
            )
        ).first()
        if existing:
            session.delete(existing)
            session.commit()
        return {"following": False}


@router.get("/profile/{username}/followers")
def get_followers(username: str):
    with Session(engine) as session:
        user = get_user_by_username(session, username)
        follows = session.exec(
            select(Follow).where(Follow.following_id == user.id)
        ).all()
        result = []
        for f in follows:
            u = session.get(User, f.follower_id)
            if u:
                try:
                    dec_name = decrypt_data(u.username)
                    prof = session.exec(
                        select(UserProfile).where(UserProfile.user_id == u.id)
                    ).first()
                    avatar = (f"/uploads/{os.path.basename(prof.avatar_path)}"
                              if prof and prof.avatar_path else None)
                    result.append({"username": dec_name, "avatar_url": avatar})
                except Exception:
                    pass
        return result


@router.get("/profile/{username}/following")
def get_following(username: str):
    with Session(engine) as session:
        user = get_user_by_username(session, username)
        follows = session.exec(
            select(Follow).where(Follow.follower_id == user.id)
        ).all()
        result = []
        for f in follows:
            u = session.get(User, f.following_id)
            if u:
                try:
                    dec_name = decrypt_data(u.username)
                    prof = session.exec(
                        select(UserProfile).where(UserProfile.user_id == u.id)
                    ).first()
                    avatar = (f"/uploads/{os.path.basename(prof.avatar_path)}"
                              if prof and prof.avatar_path else None)
                    result.append({"username": dec_name, "avatar_url": avatar})
                except Exception:
                    pass
        return result