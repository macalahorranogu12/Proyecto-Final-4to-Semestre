import os


def build_post_response(
    post,
    like_count: int = 0
):

    return {
        "id": post.id,
        "username": post.username_display,
        "image_url":
            f"/uploads/{os.path.basename(post.image_path)}",
        "title": post.title,
        "description": post.description,
        "category": post.category,
        "created_at": post.created_at.isoformat(),
        "like_count": like_count
    }


def build_comment_response(
    comment
):

    return {
        "id": comment.id,
        "username": comment.username_display,
        "content": comment.content,
        "created_at":
            comment.created_at.isoformat()
    }