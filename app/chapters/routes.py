import json

from flask import request, abort
from flask_jwt_extended import jwt_required

from app.user.utils import get_current_user_or_401, get_current_user
from app.utils import respond
from app import storage

from . import bp
from .models import Chapter, Page
from app.manga.models import Manga, Translation, MangaService


def update_data(chapter: Chapter, manga: Manga):
    name = request.form.get('name')
    tome = request.form.get('tome', type=int)
    chapter_number = request.form.get('chapter', type=int)
    team_id = request.form.get('team', type=int)

    if chapter_number is None:
        abort(respond(error="bad_request", detail={"chapter": "Chapter is required"}), status_code=400)

    chapter.name = name
    chapter.tome = tome
    chapter.chapter = chapter_number
    chapter.team_id = team_id

    if team_id:
        translation = Translation.get_by_team(manga_id=chapter.manga.id, team_id=team_id)

        if translation is None:
            translation = Translation(manga_id=chapter.manga.id, team_id=team_id)
            translation.add()
    else:
        translation = Translation.get_by_user(manga_id=manga.id, user_id=chapter.creator_id)

        if translation is None:
            translation = Translation(manga_id=chapter.manga_id, user_id=chapter.creator_id)
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
        page_filename = page.uuid + page.ext
        if page_filename not in pages_order:
            storage.delete(f"chapter/{chapter.id}/{page_filename}")
            page.delete()
            continue

        new_order = pages_order.index(page_filename)

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

    manga = MangaService.get_manga(slug=request.form.get('manga', type=str))
    if manga is None:
        return respond(error="not_found", detail={"chapter": "Manga not found"}), 404

    chapter.creator_id = current_user.id

    update_data(chapter, manga)

    if Chapter.get_by_chapter_number(chapter.translation_id, chapter.chapter) is not None:
        return abort(respond(error="bad_request", detail={"chapter": "Chapter already exists"}, status_code=400))

    chapter.add()

    update_media(chapter)
    chapter.update()

    return respond(data=chapter.to_dict()), 200

@bp.route("/<int:chapter_id>", methods=["DELETE"])
@jwt_required()
def delete_chapter(chapter_id):
    chapter = Chapter.get(chapter_id)
    current_user = get_current_user_or_401()

    if chapter is None:
        return respond(error="not_found", detail={"chapter": "Chapter not found"})

    translation = chapter.translation
    if not translation.get_permissions(current_user).get("delete"):
        return respond(error="forbidden", detail={"chapter": "Chapter is forbidden"})

    chapter.delete()

    if translation.chapters.count() == 0:
        translation.delete()

    return "", 204

@bp.route('/<int:chapter_id>', methods=['PUT'])
@jwt_required()
def put_chapter(chapter_id):
    chapter = Chapter.get(chapter_id)
    manga = chapter.translation.manga

    update_data(chapter, manga)

    update_media(chapter)

    chapter.update()

    return respond(data=chapter.to_dict()), 200

@bp.route('/<int:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    chapter = Chapter.get(chapter_id)

    if chapter is None:
        return respond(error="not_found"), 404
    return respond(data=chapter.to_dict(previous=True, next=True)), 200

@bp.route('/<int:chapter_id>/next', methods=['GET'])
def get_next_chapter(chapter_id):
    chapter = Chapter.get(chapter_id)

    if chapter is None:
        return respond(error="not_found"), 404

    return respond(data=chapter.next.to_dict(previous=True, next=True)), 200

@bp.route('/<int:chapter_id>/previous', methods=['GET'])
def get_previous_chapter(chapter_id):
    chapter = Chapter.get(chapter_id)

    if chapter is None:
        return respond(error="not_found"), 404

    return respond(data=chapter.previous.to_dict(previous=True, next=True)), 200
