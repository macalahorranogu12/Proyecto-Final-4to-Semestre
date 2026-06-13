import os
import shutil

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from sqlmodel import (
    Session,
    select
)

from models import (
    engine,
    User,
    UserProfile,
    Post,
    Comment,
    Like,
    Save,
    Follow
)

from schemas import (
    ProfileUpdate,
    FollowAction
)

from utils.helpers import (
    validate_image,
    get_user_by_username
)

from security import (
    encrypt_data,
    decrypt_data
)

from utils.profile_utils import (
    build_post_response,
    build_profile_response,
    build_user_preview
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
            select(UserProfile)
            .where(
                UserProfile.user_id
                ==
                user.id
            )
        ).first()

        if not profile:

            profile = UserProfile(
                user_id=user.id
            )

            session.add(profile)

            session.commit()

            session.refresh(
                profile
            )

        followers_count = len(
            session.exec(
                select(Follow)
                .where(
                    Follow.following_id
                    ==
                    user.id
                )
            ).all()
        )

        following_count = len(
            session.exec(
                select(Follow)
                .where(
                    Follow.follower_id
                    ==
                    user.id
                )
            ).all()
        )

        return build_profile_response(
            username,
            profile,
            followers_count,
            following_count
        )


@router.put("/profile/{username}")
def update_profile(
    username: str,
    data: ProfileUpdate
):

    with Session(engine) as session:

        user = get_user_by_username(
            session,
            username
        )

        profile = session.exec(
            select(UserProfile)
            .where(
                UserProfile.user_id
                ==
                user.id
            )
        ).first()

        if not profile:

            profile = UserProfile(
                user_id=user.id
            )

            session.add(profile)

        if data.bio is not None:
            profile.bio = data.bio

        new_name = username

        if (
            data.new_username
            and
            data.new_username.strip()
            and
            data.new_username.strip()
            !=
            username
        ):

            new_name = (
                data.new_username
                .strip()
            )

            users = session.exec(
                select(User)
            ).all()

            for u in users:

                if u.id == user.id:
                    continue

                try:

                    if (
                        decrypt_data(
                            u.username
                        )
                        ==
                        new_name
                    ):

                        raise HTTPException(
                            status_code=400,
                            detail="Nombre ocupado"
                        )

                except HTTPException:
                    raise

                except Exception:
                    pass

            user.username = encrypt_data(
                new_name
            )

        session.commit()

        return {
            "message":
            "Perfil actualizado",

            "username":
            new_name
        }


@router.post("/upload-avatar")
async def upload_avatar(
    username: str = Form(...),
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

        profile = session.exec(
            select(UserProfile)
            .where(
                UserProfile.user_id
                ==
                user.id
            )
        ).first()

        if not profile:

            profile = UserProfile(
                user_id=user.id
            )

            session.add(profile)

        ext = os.path.splitext(
            file.filename
        )[1]

        filename = (
            f"avatar_{user.id}{ext}"
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

        profile.avatar_path = (
            save_path
        )

        session.commit()

        return {
            "message":
            "Avatar actualizado",

            "avatar_url":
            f"/uploads/{filename}"
        }


@router.get(
    "/profile/{username}/liked-posts"
)
def get_liked_posts(
    username: str
):

    with Session(engine) as session:

        user = get_user_by_username(
            session,
            username
        )

        likes = session.exec(
            select(Like)
            .where(
                Like.user_id
                ==
                user.id
            )
        ).all()

        result = []

        for lk in likes:

            post = session.get(
                Post,
                lk.post_id
            )

            if post:

                result.append(
                    build_post_response(
                        post
                    )
                )

        return result


@router.get(
    "/profile/{username}/saved-posts"
)
def get_saved_posts(
    username: str
):

    with Session(engine) as session:

        user = get_user_by_username(
            session,
            username
        )

        saves = session.exec(
            select(Save)
            .where(
                Save.user_id
                ==
                user.id
            )
        ).all()

        result = []

        for sv in saves:

            post = session.get(
                Post,
                sv.post_id
            )

            if post:

                result.append(
                    build_post_response(
                        post
                    )
                )

        return result