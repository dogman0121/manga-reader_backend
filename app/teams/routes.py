from . import bp
from .models import Team

from flask import request
from flask_jwt_extended import jwt_required

from PIL import Image

from app import storage
from app.utils import respond
from app.user.utils import get_current_user_or_401

@bp.route('/', methods=['GET'], strict_slashes=False)
def index():
    pass

@bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def add_team():
    user = get_current_user_or_401()
    name = request.form.get('name')
    about = request.form.get('about')
    poster = request.files.get('poster')

    if name is None:
        return respond(error={'error': 'bad_request'}, detail={"name": "Name is required"}), 400

    team = Team(name=name, about=about, creator_id=user.id)
    team.add()

    if poster is not None:
        img = Image.open(poster)
        img.thumbnail((200, 200))
        storage.save(poster, f"/teams/{team.id}", ext=".jpg")

    return respond(data=team.to_dict()), 200

@bp.route('/<int:team_id>', methods=['GET', 'PUT'])
def get_team(team_id):
    team = Team.get(team_id)
    if team is None:
        return respond(error={'error': 'not_found'}), 404
    return respond(data=team.to_dict()), 200

@bp.route('/<int:id>/members', methods=['GET'])
def get_team_members(team_id):
    pass