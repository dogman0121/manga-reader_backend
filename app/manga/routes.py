from flask import request, jsonify
import json

from flask_jwt_extended import jwt_required, get_jwt_identity

from app.manga import bp
from app.manga.models import Manga, NameTranslation

from app.person.models import Person


@bp.route("/api/manga/add", methods=["POST"])
def add_manga():
    name = request.form.get("name")
    name_translations = json.loads(request.form.get("name_translations"))
    description = request.form.get("description")

    type_id = int(request.form.get("type"))
    status_id = int(request.form.get("status"))
    year = int(request.form.get("year"))

    adult = int(request.form.get("adult"))

    genres = request.form.getlist("genre")

    authors = request.form.getlist("author")
    artists = request.form.getlist("artist")
    publishers = request.form.getlist("publisher")

    if name is None or name == "":
        return jsonify({"msg": "Name is empty"}), 400

    manga = Manga(
        name=name,
        name_translations=[NameTranslation(lang=i["lang"], name=i["name"]) for i in name_translations],
        description=description,
        type_id=type_id,
        status_id=status_id,
        year=year,
        adult=adult,
        authors=[Person.get(int(author_id)) for author_id in authors],
        artists=[Person.get(int(artist_id)) for artist_id in artists],
        publishers=[Person.get(int(publisher_id)) for publisher_id in publishers],
        creator_id=1#get_jwt_identity()
    )

    print(manga)

    return "", 204
