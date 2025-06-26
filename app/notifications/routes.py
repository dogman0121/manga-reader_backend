from . import bp

from app.user.utils import get_current_user_or_401

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .models import Notification
from ..utils import respond

@bp.route('', strict_slashes=False, methods=['GET'])
@jwt_required()
def get_notification():
    page = request.args.get('page', 1, type=int)

    current_user = get_current_user_or_401()

    notifications = Notification.get_user_notifications(current_user, page=page)

    return respond(data=[i.to_dict() for i in notifications])

@bp.route('', strict_slashes=False, methods=['POST'])
def add_notification():
    pass

@bp.route('', strict_slashes=False, methods=['DELETE'])
def remove_notification():
    pass

@bp.route('', strict_slashes=False, methods=['PATCH'])
def read_notification():
    pass

@bp.route('', strict_slashes=False, methods=['PUT'])
def update_notification():
    pass