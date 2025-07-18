import json
import os
from flask import request, abort
from flask_jwt_extended import jwt_required

from app.user.utils import get_current_user_or_401, get_current_user
from app.utils import respond
from app import storage, db

from . import bp
from .models import Chapter, Page
from app.manga.models import Translation
from app.manga.services import MangaService, TranslationService
from app.teams.models import Team
from .services import ChapterService
from ..logs import log_runtime, app_logger
from ..user.models import UserService


def update_data(chapter: Chapter):
    name = request.form.get('name')
    tome = request.form.get('tome', type=int)
    chapter_number = request.form.get('chapter', type=int)

    if chapter_number is None:
        abort(respond(error="bad_request", detail={"chapter": "Chapter is required"}), status_code=400)

    chapter.name = name
    chapter.tome = tome
    chapter.chapter = chapter_number

def delete_page(chapter, page):
    page_filename = page.uuid + page.ext

    storage.delete(f"chapter/{chapter.id}/{page_filename}")
    page.delete()

def save_page(chapter, page, order):
    orig_filename = page.filename

    uuid = storage.save(page, f"chapter/{chapter.id}", ext=".webp")

    chapter.pages.append(Page(
        orig_filename=orig_filename,
        uuid=uuid,
        chapter_id=chapter.id,
        ext=".webp",
        order=order
    ))


def update_media(chapter: Chapter):
    new_pages = request.files.getlist('new_page')
    pages_order = request.form.get('pages_order')

    pages_order = [] if pages_order is None else json.loads(pages_order)

    app_logger.info(f"update_media: Found {len(new_pages)} new pages of {len(pages_order)} pages")

    # update existing pages
    for page in chapter.pages:
        # delete unused pages
        if page.uuid not in pages_order:
            delete_page(chapter, page)
            continue

        new_order = pages_order.index(page.uuid)

        page.order = new_order
        page.update()

    # add new_pages
    for page in new_pages:
        try:
            filename, _ = os.path.splitext(page.filename)
            order = pages_order.index(filename)

            save_page(chapter, page, order)
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
    current_user = get_current_user()
    chapter = Chapter(creator_id=current_user.id, creator=current_user)

    manga_slug = request.form.get('manga', type=str)
    team_id = request.form.get('team', type=int)
    user_id = request.form.get('user', type=int)

    if manga_slug is None:
        return respond(error="bad_request", detail={"chapter": "Manga is required"}), 400

    if team_id and user_id:
        return respond(error="bad_request", detail={"chapter": "Team or User required"}), 400

    manga = MangaService.get_manga(slug=manga_slug)
    if manga is None:
        return respond(error="not_found", detail={"chapter": "Manga not found"}), 404

    team = Team.get(team_id)
    user = UserService.get_user(user_id=user_id)

    translation = TranslationService.get_or_create_translation(manga=manga, team=team, user=user)
    chapter.translation = translation

    update_data(chapter)

    if Chapter.get_by_chapter_number(translation.id, chapter.chapter) is not None:
        return abort(respond(error="bad_request", detail={"chapter": "Chapter already exists"}, status_code=400))

    ChapterService.create_chapter(chapter)

    update_media(chapter)

    db.session.commit()

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
@log_runtime
@jwt_required()
def put_chapter(chapter_id):
    app_logger.info("put_chapter: Request came")
    chapter = Chapter.get(chapter_id)
    manga = chapter.translation.manga
    current_user = get_current_user()

    if chapter is None:
        return respond(error="not_found", detail={"chapter": "Chapter not found"}), 404

    update_data(chapter)

    team = Team.get(request.form.get('team_id', type=int))
    user = UserService.get_user(user_id=chapter.creator_id)

    if user and current_user.id == chapter.translation.user.id:
        new_translation = TranslationService.get_or_create_translation(manga=manga, user=user)
        chapter.translation = new_translation
    elif team and chapter.translation.team.creator_id == current_user.id:
        new_translation = TranslationService.get_or_create_translation(manga=manga, team=team)
        chapter.translation = new_translation

    app_logger.info(f"put_chapter: Received {len(request.files.getlist('new_page'))} files")
    update_media(chapter)

    db.session.commit()

    app_logger.info("put_chapter: Chapter updated")

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
