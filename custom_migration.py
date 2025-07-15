import uuid

from app import db, manga
from app.comments.models import MangaComment, Comment
from app.manga.models import Poster, Manga, PosterFile
from manage import app
from sqlalchemy import text
from PIL import Image
from pytils.translit import slugify

with app.app_context():
    # db.session.execute(text("""DELETE FROM manga_poster WHERE manga_poster.uuid='45974b53-c93e-4c97-90fa-448cd07b0947';"""))
    # db.session.commit()
    print(db.session.execute(text("""SELECT * FROM chapter WHERE tome=1 AND chapter=1;""")).all())
    #db.session.commit()