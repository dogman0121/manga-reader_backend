from flask import request, jsonify
import json
import os

from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.manga import bp
from app.manga.models import Manga, NameTranslation, Genre, Adult, Type, Status, Poster, Background
from app.person.models import Person

from app.manga.utils import get_uuid4_filename

def validate_manga(manga):
    if not manga.name:
        return False, "Name is empty"

    return True, ""


def update_data(manga: Manga) -> None:
    name = request.form.get("name")

    if request.form.get("name-translations") is not None:
        name_translations = json.loads(request.form.get("name-translations"))
    else:
        name_translations = {}

    description = request.form.get("description")

    type = Type.query.get(int(request.form.get("type") or 1))
    status = Status.query.get(int(request.form.get("status") or 1))
    year = int(request.form.get("year") or 0)

    adult = Adult.query.get(int(request.form.get("adult") or 2025))

    genres = [Genre.query.get(int(i)) for i in request.form.getlist("genre")]

    authors = [Person.get(int(i)) for i in request.form.getlist("author")]
    artists = [Person.get(int(i)) for i in request.form.getlist("artist")]
    publishers = [Person.get(int(i)) for i in request.form.getlist("publisher")]

    manga.name = name
    manga.name_translations = [NameTranslation(lang=lang, name=name) for lang, name in name_translations.items()]
    manga.description = description
    manga.type = type
    manga.status = status
    manga.year = year
    manga.adult = adult
    manga.genres = genres
    manga.authors = authors
    manga.artists = artists
    manga.publishers = publishers


def update_media(manga: Manga) -> None:
    try:
        os.mkdir("app/static/manga/{}".format(manga.id))
    except FileExistsError:
        pass

    if request.files.get("background") is not None:
        background_file = request.files.get("background")
        background_filename = get_uuid4_filename() + ".jpg"
        background_file.save(f"app/static/manga/{manga.id}/{background_filename}")
        manga.background = Background(filename=background_filename)

    posters = []
    for order, file in enumerate(request.files.getlist("posters")):
        poster_filename = get_uuid4_filename() + ".jpg"
        file.save(f"app/static/manga/{manga.id}/{poster_filename}")
        posters.append(Poster(filename=poster_filename, order=order))
    manga.posters = posters

    if manga.posters:
        manga.main_poster_number = int(request.form.get("main-poster") or (len(manga.posters) - 1))


@bp.route('/api/manga/<int:manga_id>', methods=['GET'])
def get_manga(manga_id):
    manga = Manga.get(manga_id)
    return jsonify(manga.to_dict())

@bp.route("/api/manga/add", methods=["POST"])
@jwt_required()
def add_manga():
    name = request.form.get("name")

    if name is None or name == "":
        return jsonify({"msg": "Name is empty"}), 400

    manga = Manga()

    update_data(manga)

    manga.add()

    update_media(manga)

    manga.update()

    return "", 201
