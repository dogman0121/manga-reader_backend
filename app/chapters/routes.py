import json

from flask import request, abort
from flask_jwt_extended import jwt_required

from app.user.utils import get_current_user_or_401, get_current_user
from app.utils import respond
from app import storage

from . import bp
from .models import Chapter, Page
from app.manga.models import Manga, Translation


def update_data(chapter: Chapter):
    name = request.form.get('name')
    tome = request.form.get('tome', type=int)
    chapter_number = request.form.get('chapter', type=int)
    team_id = request.form.get('team', type=int)
    manga_id = request.form.get('manga', type=int)

    if chapter_number is None:
        abort(respond(error="bad_request", detail={"chapter": "Chapter is required"}), status_code=400)

    chapter.name = name
    chapter.tome = tome
    chapter.chapter = chapter_number
    chapter.team_id = team_id

    if Manga.get(manga_id) is None:
        abort(respond(error="bad_request", detail={"manga": "Manga not found"}, status_code=400))

    chapter.manga_id = manga_id

    if team_id:
        translation = Translation.get_by_team(manga_id=manga_id, team_id=team_id)

        if translation is None:
            translation = Translation(manga_id=manga_id, team_id=team_id)
            translation.add()
    else:
        translation = Translation.get_by_user(manga_id=manga_id, user_id=chapter.creator_id)

        if translation is None:
            translation = Translation(manga_id=manga_id, user_id=chapter.creator_id)
            translation.add()

    chapter.translation_id = translation.id

def update_media(chapter: Chapter):
    new_pages = request.files.getlist('new_page')
    pages_order = request.form.get('pages_order')

    if pages_order is None:
        pages_order = []
    else:
        pages_order = json.loads(pages_order)


    # update existing pages
    for page in chapter.pages:
        # delete unused pages
        if page.uuid + page.ext not in pages_order:
            storage.delete(f"chapter/{chapter.id}/{page.uuid}{page.ext}")
            page.delete()

        new_order = pages_order.index(page.uuid)

        page.order = new_order
        page.update()

    # add new_pages
    for page in new_pages:
        try:
            order = pages_order.index(page.filename)

            uuid = storage.save(page, f"chapter/{chapter.id}", ext=".webp")

            page = Page(uuid=uuid, chapter_id=chapter.id, ext=".webp", order=order)
            page.add()
        except ValueError:
            continue

@bp.route('', methods=['GET'], strict_slashes=False)
def index():
    translation_id = request.args.get("translation", type=int)

    if translation_id:
        translation = Translation.get(translation_id)
        return respond(data=[i.to_dict() for i in translation.chapters])
    else:
        return respond(error="bad_request", detail={"chapter": "Chapter is required"})

@bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required()
def post_chapter():
    current_user = get_current_user_or_401()

    chapter = Chapter(creator_id=current_user.id, creator=current_user)
    update_data(chapter)

    chapter.add()

    update_media(chapter)
    chapter.update()

    return respond(data=chapter.to_dict()), 200


@bp.route('/<int:chapter_id>', methods=['PUT'])
@jwt_required()
def put_chapter(chapter_id):
    chapter = Chapter.get(chapter_id)

    update_data(chapter)

    update_media(chapter)

    chapter.update()

    return respond(data=chapter.to_dict()), 200

@bp.route('/<int:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    chapter = Chapter.get(chapter_id)

    if chapter is None:
        return respond(error="not_found"), 404
    return respond(data=chapter.to_dict()), 200

@bp.route('/<int:chapter_id>/next', methods=['GET'])
def get_next_chapter(chapter_id):
    chapter = Chapter.get(chapter_id)

    if chapter is None:
        return respond(error="not_found"), 404

    return respond(data=chapter.next), 200

@bp.route('/<int:chapter_id>/previous', methods=['GET'])
def get_previous_chapter(chapter_id):
    chapter = Chapter.get(chapter_id)

    if chapter is None:
        return respond(error="not_found"), 404

    return respond(data=chapter.previous), 200
