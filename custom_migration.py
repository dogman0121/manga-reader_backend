import uuid

from app import db, manga
from app.comments.models import MangaComment, Comment
from app.manga.models import Poster, Manga, PosterFile
from manage import app
from sqlalchemy import text
from PIL import Image
from pytils.translit import slugify

with app.app_context():
    print(db.session.execute(text("""SELECT * FROM list_manga""")).all())
