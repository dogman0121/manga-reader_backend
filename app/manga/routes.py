from flask import request, jsonify
import json
import os

from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.user.models import User
from app.manga import bp
from app.manga.models import Manga, NameTranslation, Genre, Adult, Type, Status, Poster, Background
from app.person.models import Person

from app.manga.utils import get_uuid4_filename

def validate_manga():
    if not request.form.get("name"):
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
    manga.name_translations = [
        NameTranslation(lang=lang, name=name)
        for lang, name in name_translations.items()
    ]
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
    if request.form.get("posters_order") is not None:
        posters_order = json.loads(request.form.get("posters_order"))
    else:
        posters_order = []

    new_posters = request.files.getlist("new_posters")

    posters_list = []

    for poster in manga.posters:
        if poster.filename in posters_order:
            poster.order = posters_order.index(poster.filename)
            posters_list.append(poster)
        else:
            os.remove("app/static/manga/" + poster.filename)

    for new_poster in new_posters:
        new_filename = get_uuid4_filename() + ".jpg"
        new_poster.save("app/static/manga/" + new_filename)
        posters_list.append(Poster(filename=new_filename, order=posters_order.index(new_poster.filename)))

    manga.posters = posters_list

    if len(posters_list) > 0:
        manga.main_poster_number = int(request.form.get("main_poster") or len(manga.posters)-1)


@bp.route('/api/manga/<int:manga_id>', methods=['GET'])
@jwt_required(optional=True)
def get_manga(manga_id):
    user_id = get_jwt_identity()

    user = User.get_by_id(user_id) if user_id else None

    manga = Manga.get(manga_id)

    if manga is None:
        return jsonify(msg="Not found"), 404

    return jsonify(manga.to_dict(user))


@bp.route("/api/manga/add", methods=["POST"])
@jwt_required()
def add_manga():
    result, message = validate_manga()
    if not result:
        return jsonify(msg=message), 400


    manga = Manga()
    manga.creator_id = get_jwt_identity()

    update_data(manga)

    update_media(manga)

    manga.add()

    return jsonify(manga.to_dict(User.get_by_id(get_jwt_identity()))), 201
