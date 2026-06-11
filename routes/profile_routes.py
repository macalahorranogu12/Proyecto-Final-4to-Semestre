import os
import shutil

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
    UserProfile
)

from utils.helpers import (
    validate_image,
    get_user_by_username
)

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.get("/profile/{username}")
def get_profile(username: str):

    with Session(engine) as session:

        user = get_user_by_username(
            session,
            username
        )

        profile = session.exec(
            select(UserProfile).where(
                UserProfile.user_id == user.id
            )
        ).first()

        if not profile:

            profile = UserProfile(
                user_id=user.id
            )

            session.add(profile)
            session.commit()
            session.refresh(profile)

        return {
            "username": username,
            "avatar_url":
                f"/uploads/{os.path.basename(profile.avatar_path)}"
                if profile.avatar_path else None,
            "bio": profile.bio
        }


@router.post("/upload-avatar")
async def upload_avatar(
    username: str = Form(...),
    file: UploadFile = File(...)
):

    validate_image(file.filename)

    with Session(engine) as session:

        user = get_user_by_username(
            session,
            username
        )

        profile = session.exec(
            select(UserProfile).where(
                UserProfile.user_id == user.id
            )
        ).first()

        if not profile:
            profile = UserProfile(
                user_id=user.id
            )
            session.add(profile)

        ext = os.path.splitext(
            file.filename
        )[1].lower()

        filename = (
            f"avatar_{user.id}{ext}"
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

        profile.avatar_path = save_path

        session.commit()

        return {
            "message":
                "Avatar actualizado",
            "avatar_url":
                f"/uploads/{filename}"
        }