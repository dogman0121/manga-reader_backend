import uuid

from flask import request
import json
import os
from pytils.translit import slugify

from flask_jwt_extended import jwt_required, get_jwt_identity

from app import storage

from app.user.models import User
from . import bp
from .models import MangaService, Manga, NameTranslation, Genre, Adult, Type, Status, Poster, Rating, PosterFile

from flask import abort
from app.manga.utils import get_uuid4_filename

from PIL import Image

from ..user.utils import get_current_user
from ..utils import respond


def validate_manga():
    if not request.form.get("name"):
        return abort(respond(error="bad_request", detail={"name": "Name is empty"}, status_code=400))

    return True, ""


def update_data(manga: Manga) -> None:
    name = request.form.get("name")

    if request.form.get("name-translations") is not None:
        name_translations = json.loads(request.form.get("name-translations"))
    else:
        name_translations = {}

    description = request.form.get("description")

    type = Type.query.get(int(request.form.get("type") or 1), )
    status = Status.query.get(int(request.form.get("status") or 1), )
    year = int(request.form.get("year") or 0)

    adult = Adult.query.get(int(request.form.get("adult") or 2025), )

    genres = [Genre.get(int(i)) for i in request.form.getlist("genres")]

    authors = [User.get_by_id(int(i)) for i in request.form.getlist("authors")]
    artists = [User.get_by_id(int(i)) for i in request.form.getlist("artists")]
    publishers = [User.get_by_id(int(i)) for i in request.form.getlist("publishers")]

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

poster_sizes = {
    "thumbnail": (80, 120),
    "small": (200, 300),
    "medium": (400, 600),
    "large": (600, 900),
}

def save_image(img, size, manga_id):
    ratio = img.size[0] / img.size[1]

    if ratio < 1:
        new_height = size[1]
        new_width = int(size[1] * ratio)
    else:
        new_height = int(size[0] * ratio)
        new_width = size[0]

    new_img = img.copy().convert("RGB")
    new_img.thumbnail((new_width, new_height))
    return storage.save(new_img, f"manga/{manga_id}", ext=".jpg")

background_size = (1600, 900)

def create_upload_folder(manga_id) -> None:
    if not os.path.exists(f'app/static/manga/{manga_id}'):
        os.makedirs(f'app/static/manga/{manga_id}')

def update_media(manga: Manga) -> None:
    create_upload_folder(manga.id)

    # Save posters
    if request.form.get("posters_order") is not None:
        posters_order = json.loads(request.form.get("posters_order"))
    else:
        posters_order = []

    new_posters = request.files.getlist("new_posters")

    for poster in manga.posters:
        if poster.uuid in posters_order:
            poster.order = posters_order.index(poster.uuid)
        else:
            manga.posters.remove(poster)
            poster.delete()

    for new_poster in new_posters:
        old_filename = new_poster.filename
        source_img = Image.open(new_poster)

        poster_uuid = str(uuid.uuid4())

        poster = Poster(
            uuid=poster_uuid,
            manga_id=manga.id,
            order=posters_order.index(old_filename)
        )

        for name, size in poster_sizes.items():
            identifier = save_image(source_img, size, manga.id)

            poster.files.append(
                PosterFile(
                    uuid=identifier,
                    ext=".jpg",
                    type=name,
                )
            )

        orig_uuid = save_image(source_img, source_img.size, manga.id)
        poster.files.append(
            PosterFile(
                uuid=orig_uuid,
                ext=".jpg",
                type="original",
            )
        )
        poster.add()

    # Save main poster
    if len(manga.posters) > 0:
        main_poster = request.form.get("main_poster")
        if main_poster in posters_order:
            manga.main_poster_number = posters_order.index(main_poster)
        else:
            manga.main_poster_number = len(manga.posters)-1

    # Save background image
    background = request.files.get("background")
    if background is not None:
        try:
            os.remove(f"app/static/manga/{manga.id}/{manga.background}")
        except FileNotFoundError:
            pass

        bg_image = Image.open(background)
        bg_image.thumbnail(background_size)

        filename = get_uuid4_filename() + ".jpg"
        bg_image.save(f"app/static/manga/{manga.id}/" + filename)
        manga.background = filename


@bp.route('/api/v1/manga/<slug>', methods=['GET'])
@jwt_required(optional=True)
def get_manga_v1(slug):
    current_user = get_current_user()

    manga = MangaService.get_by_slug(slug)

    if manga is None:
        return respond(error="not_found"), 404

    manga.views += 1
    manga.update()

    return respond(data=manga.to_dict(user=current_user, posters=True))


@bp.route("/api/v1/manga", methods=["POST"])
@jwt_required()
def add_manga_v1():
    result, message = validate_manga()
    if not result:
        return respond(error="bad_request"), 400

    current_user = get_current_user()

    manga = Manga()
    manga.creator_id = current_user.id

    update_data(manga)

    slug = slugify(manga.name)
    if MangaService.get_by_slug(slug) is None:
        manga.slug = slug

    manga.add()

    update_media(manga)
    manga.update()

    return respond(data=manga.to_dict(current_user)), 201


@bp.route("/api/v1/manga/<slug>", methods=["PUT"])
@jwt_required()
def edit_manga_v1(slug) -> [str, int]:
    manga = MangaService.get_by_slug(slug)
    user = User.get_by_id(get_jwt_identity())

    if manga is None:
        return respond(error="not_found"), 404

    if not manga.can_edit(user=user):
        return respond(error="forbidden"), 403

    update_data(manga)
    update_media(manga)

    manga.update()

    return respond(data=manga.to_dict(user=User.get_by_id(get_jwt_identity()), posters=True)), 200


@bp.route("/api/v1/manga/<slug>", methods=["DELETE"])
@jwt_required()
def delete_manga_v1(slug) -> [str, int]:
    pass


@bp.route("/api/v1/manga/<slug>/ratings", methods=["POST"])
@jwt_required()
def add_rating_v1(slug) -> [str, int]:
    rating = request.json.get("rating")

    if rating is None:
        return respond(error="bad_request"), 400

    try:
        rating_int = int(rating)
    except ValueError:
        return respond(error="bad_request"), 400

    manga = MangaService.get_by_slug(slug)
    if manga is None:
        return respond(error="not_found"), 404

    user = User.get_by_id(get_jwt_identity())
    if Rating.get(user.id, manga.id) is None:
        manga.add_rating(user, rating_int)
    else:
        if rating_int == Rating.get(user.id, manga.id).rating:
            manga.delete_rating(user)
        else:
            manga.update_rating(user, rating_int)

    return respond(data=None, error=None), 201


@bp.route("/api/v1/manga/<slug>/ratings", methods=["DELETE"])
@jwt_required()
def delete_rating_v1(slug) -> [str, int]:
    manga = MangaService.get_by_slug(slug)

    if manga is None:
        return respond("not_found"), 404

    user = User.get_by_id(get_jwt_identity())
    manga.remove_rating(user)

    return respond(data=None, error=None), 200