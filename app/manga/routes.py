from flask import request, jsonify
import json
import os

from werkzeug.utils import secure_filename

from flask_jwt_extended import jwt_required, get_jwt_identity

from app.manga import bp
from app.manga.models import Manga, NameTranslation

from app.person.models import Person


@bp.route('/api/manga/<int:manga_id>', methods=['GET'])
def get_manga(manga_id):
    manga = Manga.get(manga_id)
    return jsonify(manga.to_dict())

@bp.route("/api/manga/add", methods=["POST"])
@jwt_required()
def add_manga():
    name = request.form.get("name")

    if request.form.get("name-translations") is not None:
        name_translations = json.loads(request.form.get("name-translations"))
    else:
        name_translations = {}

    description = request.form.get("description")

    type_id = int( request.form.get("type") or 1)
    status_id = int( request.form.get("status") or 1)
    year = int(request.form.get("year") or 1)

    adult_id = int(request.form.get("adult") or 1)

    genres = request.form.getlist("genre")

    authors = request.form.getlist("author")
    artists = request.form.getlist("artist")
    publishers = request.form.getlist("publisher")


    if name is None or name == "":
        return jsonify({"msg": "Name is empty"}), 400

    manga = Manga(
        name=name,
        name_translations=[NameTranslation(lang=key, name=value) for key, value in name_translations],
        description=description,
        status_id=status_id,
        type_id=type_id,
        year=year,
        genres=genres,
        adult_id=adult_id,
        authors=[Person.get(int(author_id)) for author_id in authors],
        artists=[Person.get(int(artist_id)) for artist_id in artists],
        publishers=[Person.get(int(publisher_id)) for publisher_id in publishers],
        creator_id=get_jwt_identity()
    )

    manga.add()

    os.mkdir(os.path.join(os.getcwd(), "app\static\manga\{}".format(manga.id)))
    os.mkdir(os.path.join(os.getcwd(), "app\static\manga\{}\posters".format(manga.id)))

    if request.files.get("main-poster") is not None:
        request.files.get("main-poster").save(f"app/static/manga/{manga.id}/main-poster.jpg")

    if request.files.get("wrapper") is not None:
        request.files.get("wrapper").save(f"app/static/manga/{manga.id}/wrapper.jpg")

    for file in request.files.getlist("posters"):
        file.save(f"app/static/manga/{manga.id}/posters/{secure_filename(file.filename)}")

    # print(manga.id)

    return "", 204
