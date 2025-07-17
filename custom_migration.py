import uuid

from app import db, manga
from app.chapters.models import Page
from app.comments.models import MangaComment, Comment
from app.manga.models import Poster, Manga, PosterFile
from manage import app
from sqlalchemy import text
from PIL import Image
from pytils.translit import slugify

with app.app_context():
    for p in Page.query.all():
        p.orig_filename = p.uuid + p.ext

    db.session.commit()