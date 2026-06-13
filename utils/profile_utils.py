import os


def build_post_response(post):

    return {
        "id": post.id,
        "username": post.username_display,
        "image_url":
            f"/uploads/{os.path.basename(post.image_path)}",
        "title":
            post.title,
        "description":
            post.description,
        "category":
            post.category,
        "created_at":
            post.created_at.isoformat(),
        "like_count": 0
    }


def build_profile_response(
    username,
    profile,
    followers_count,
    following_count
):

    avatar = None

    if (
        profile
        and
        profile.avatar_path
    ):

        avatar = (
            f"/uploads/"
            f"{os.path.basename(profile.avatar_path)}"
        )

    return {

        "username":
            username,

        "avatar_url":
            avatar,

        "bio":
            profile.bio,

        "is_adult":
            bool(
                profile.is_adult
            ),

        "followers_count":
            followers_count,

        "following_count":
            following_count
    }


def build_user_preview(
    username,
    avatar_path=None
):

    avatar = None

    if avatar_path:

        avatar = (
            f"/uploads/"
            f"{os.path.basename(avatar_path)}"
        )

    return {

        "username":
            username,

        "avatar_url":
            avatar
    }