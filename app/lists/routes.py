from flask_jwt_extended import jwt_required

from . import bp
from .models import ListTitle, ListService, List
from ..manga.models import MangaService
from ..user.utils import get_current_user
from ..utils import respond

from app import db
from flask import request

@bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_lists():
    current_user = get_current_user()

    return respond(data=[l.to_dict() for l in current_user.lists])

@bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required()
def add_list():
    current_user = get_current_user()
    name = request.form.get('name')
    description = request.form.get('description')

    lst = List(name=name, description=description, creator=current_user)
    db.session.add(lst)
    db.session.commit()

    return respond(data=lst.to_dict())

@bp.route('/<int:list_id>', methods=['PUT'])
@jwt_required()
def update_list(list_id):
    current_user = get_current_user()
    name = request.form.get('name')
    description = request.form.get('description')

    lst = ListService.get_list(list_id=list_id)
    if current_user.id != lst.creator_id:
        return respond(error="forbidden"), 403

    lst.name = name or lst.name
    lst.description = description or lst.description
    db.session.commit()

@bp.route('/<int:list_id>', methods=['GET'])
def get_list(list_id):
    lst = ListService.get_list(list_id=list_id)

    return respond(data=lst.to_dict())

@bp.route('/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_list(list_id):
    current_user = get_current_user()
    lst = ListService.get_list(list_id=list_id)
    if current_user.id != lst.creator_id:
        return respond(error="forbidden"), 403

    db.session.delete(lst)
    db.session.commit()

@bp.route('/<int:list_id>/titles', methods=['PUT'])
@jwt_required()
def add_titles(list_id):
    lst = ListService.get_list(list_id)

    if lst is None:
        return respond(error="not_found"), 404

    manga_list = request.json.get('manga', [])
    if manga_list is None:
        return respond(error="bad_request", detail={"titles": "Titles is empty"}), 400

    for manga_id in manga_list:
        manga = MangaService.get_manga(manga_id=manga_id)
        if manga is None:
            return respond(error="not_found"), 404
        lst.add_manga(manga)

    db.session.commit()
    return {}, 200

@bp.route('/<int:list_id>/titles', methods=['DELETE'])
@jwt_required()
def delete_titles(list_id):
    lst = ListService.get_list(list_id)

    if lst is None:
        return respond(error="not_found"), 404

    manga_list = request.json.get('manga', [])
    if manga_list is None:
        return respond(error="bad_request", detail={"titles": "Titles is empty"}), 400

    for manga_id in manga_list:
        manga = MangaService.get_manga(manga_id=manga_id)
        if manga is None:
            return respond(error="not_found"), 404
        lst.remove_manga(manga)

    db.session.commit()
    return {}, 200