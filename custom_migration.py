from app import db
from app.comments.models import MangaComment, Comment
from app.manga.models import Poster
from manage import app

with app.app_context():
    for manga_comment in MangaComment.query.all():
        manga_id = manga_comment.manga_id
        comment_id = manga_comment.comment_id

        comment = Comment.get(comment_id)

        comment.entity_id = manga_id
        comment.entity_type = "manga"

        comment.update()