from flask import request, jsonify
import json
import os

from flask_jwt_extended import jwt_required, get_jwt_identity

from app.user.models import User
from app.manga import bp
from app.manga.models import Manga, NameTranslation, Genre, Adult, Type, Status, Poster
from app.person.models import Person

from app.manga.utils import get_uuid4_filename

from PIL import Image

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

sizes = {
    "thumbnail": (70, 100),
    "small": (350, 500),
    "medium": (700, 1000),
    "large": (1400, 2100),
}

def create_upload_folder(manga_id) -> None:
    if not os.path.exists(f'app/static/manga/{manga_id}'):
        os.mkdir(f'app/static/manga/{manga_id}')

def update_media(manga: Manga) -> None:
    create_upload_folder(manga.id)

    # Save posters
    if request.form.get("posters_order") is not None:
        posters_order = json.loads(request.form.get("posters_order"))
    else:
        posters_order = []

    new_posters = request.files.getlist("new_posters")

    posters_list = []

    for poster in manga.posters:
        if poster.filename["filename"] in posters_order:
            poster.order = posters_order.index(poster.filename["filename"])
            posters_list.append(poster)
        else:
            for filename in poster.filename.values():
                if os.path.exists(f"app/static/manga/{manga.id}/" + filename):
                    os.remove(f"app/static/manga/{manga.id}/" + filename)

    for new_poster in new_posters:
        old_filename = os.path.splitext(new_poster.filename)[0]
        identifier = get_uuid4_filename()
        #####
        source_img = Image.open(new_poster)
        json_data = {"filename": identifier}

        for name, size in sizes.items():
            new_img = source_img.copy().convert("RGB")
            new_img.thumbnail(size)
            filename = identifier + "_" + name + ".jpg"
            json_data[name] = filename
            new_img.save(f"app/static/manga/{manga.id}/" + filename)
        #####

        posters_list.append(Poster(filename=json_data, order=posters_order.index(old_filename)))
    manga.posters = posters_list

    # Save main poster
    if len(posters_list) > 0:
        main_poster = request.form.get("main_poster")
        if main_poster in posters_order:
            manga.main_poster_number = posters_order.index(main_poster)
        else:
            manga.main_poster_number = len(posters_list)-1

    # Save background image
    background = request.form.get("background")
    if background is not None:
        filename = get_uuid4_filename()
        background.save(f"app/static/manga/{manga.id}/" + filename + ".jpg")




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
    manga.add()

    update_media(manga)
    manga.update()

    return jsonify(manga.to_dict(User.get_by_id(get_jwt_identity()))), 201


@bp.route("/api/manga/<int:manga_id>/edit", methods=["PUT"])
@jwt_required()
def edit_manga(manga_id: int) -> [str, int]:
    manga = Manga.get(manga_id)
    user = User.get_by_id(get_jwt_identity())

    if manga is None:
        return jsonify(msg="Not found"), 404

    if not manga.can_edit(user=user):
        return jsonify(msg="Not allowed"), 403

    update_data(manga)
    update_media(manga)

    manga.update()

    return jsonify(manga.to_dict(User.get_by_id(get_jwt_identity()))), 200
