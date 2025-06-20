import uuid

from app import db, manga
from app.comments.models import MangaComment, Comment
from app.manga.models import Poster, Manga, PosterFile
from manage import app
from sqlalchemy import text
from PIL import Image

with app.app_context():
    for manga in Manga.query.all():
        order = 0
        posters = []
        new_poster = Poster(uuid= str(uuid.uuid4()),manga_id=manga.id, order=order)
        for poster in sorted(manga.posters, key=lambda x: x.order):
            if poster.order == order:
                new_poster.files.append(PosterFile(
                    uuid=poster.uuid,
                    ext=".jpg",
                ))
            else:
                posters.append(new_poster)
                order += 1
                new_poster = Poster(uuid=str(uuid.uuid4()), manga_id=manga.id, order=order)
            poster.delete()
        if len(new_poster.files) != 0:
            posters.append(new_poster)
        manga.posters = posters
        manga.update()
