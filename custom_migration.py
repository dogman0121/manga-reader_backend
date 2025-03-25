from app import db
from app.manga.models import Poster
from manage import app

with app.app_context():
    for poster in Poster.query.all():
        poster.uuid = poster.filename["filename"]

        new_dict = poster.filename.copy()
        del new_dict["filename"]

        poster.filenames = new_dict
        poster.update()