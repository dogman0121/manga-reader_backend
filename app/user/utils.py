from flask import abort
from flask_jwt_extended import (get_jwt_identity)
from .models import User


def get_current_user():
    user_id = get_jwt_identity()

    user = User.get_by_id(user_id)

    return user

def get_current_user_or_401():
    user_id = get_jwt_identity()

    user = User.get_by_id(user_id)
    if user is None:
        abort(401, {"error": {"code": "unauthorized"}})

    return user