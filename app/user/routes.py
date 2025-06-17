from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required
)
from app import storage
from app.user import bp
from app.user.models import User, Avatar
from app.notifications.models import Notification
from app.email import send_registration_verification_mail, send_password_recovery_mail
from PIL import Image

from app.utils import respond


@bp.route('/api/v1/users/<int:user_id>', methods=['GET'])
@jwt_required(optional=True)
def get_user_v1(user_id: int):
    user = User.get_by_id(user_id)
    current_user = User.get_by_id(get_jwt_identity())

    if user is None:
        return jsonify(data=None, error={"code": "not_found"}), 404
    return jsonify(data = user.to_dict(user=current_user)), 200

@bp.route('/api/v1/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user_v1(user_id: int):
    user = User.get_by_id(user_id)
    current_user = User.get_by_id(get_jwt_identity())

    if user.id != current_user.id:
        return jsonify(data=None, error={"code": "forbidden"}), 403

    avatar = request.files.get('avatar')
    if avatar is not None:
        new_file = Image.open(avatar).convert('RGB')
        new_file.filename = avatar.filename
        new_file.thumbnail((120, 120))

        filename = storage.save(new_file, f"user/{user_id}")

        if user.avatar is not None:
            storage.delete(f"user/{user.id}/{user.avatar.filename}")
            user.avatar.filename = filename
        else:
            user.avatar = Avatar(filename=filename)

    login = request.form.get('login')
    if login is not None:
        user.login = login

    about = request.form.get('about')
    if about is not None:
        user.about = about

    user.update()

    return jsonify(data=user.to_dict(current_user)), 200


@bp.route('/api/v1/users/<int:user_id>/subscribe', methods=['POST', 'DELETE'])
@jwt_required()
def subscribe_v1(user_id: int):
    user = User.get_by_id(user_id)
    subscriber = User.get_by_id(get_jwt_identity())

    if user.id == subscriber.id:
        return jsonify(data=None, error={"code": "forbidden"}), 403

    if user is None:
        return jsonify(data=None, error={"code": "not_found"}), 404

    if subscriber is None:
        return jsonify(data=None, error={"code": "not_found"}), 404

    if request.method == 'POST':
        user.subscribe(subscriber)
        notification = Notification(
            type="user",
            action="subscribe",
            user=user,
            actor=subscriber
        )
        notification.add()
        return jsonify({"error": None, "data": None}), 200
    elif request.method == 'DELETE':
        user.unsubscribe(subscriber)
        return jsonify({"error": None, "data": None}), 200

@bp.route('/api/v1/users/<int:user_id>/subscribers', methods=['GET'])
@jwt_required(optional=True)
def get_subscribers_v1(user_id: int):
    user = User.get_by_id(user_id)

    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id) if current_user_id else None

    page = request.args.get('page', 1, type=int)

    if user is None:
        return jsonify(data=None, error={"code": "not_found"}), 404

    subscribers = user.get_subscribers(page=page, per_page=20)

    return jsonify(data=[i.to_dict(current_user) for i in subscribers]), 200

@bp.route('/api/v1/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def edit_user_v1(user_id: int):
    user = User.get_by_id(int(get_jwt_identity()))

    if user.id != user_id:
        return respond(error="forbidden", detail={"msg": "You are not allowed to edit this user"}), 403

    if "login" in request.json:
        user.login = request.json["login"]

    if "password" in request.json:
        user.password = request.json["password"]

    user.update()
    return respond(data=user.to_dict())

@bp.route('/api/v1/users/me', methods=['GET'])
@jwt_required()
def get_current_user_v1():
    user = get_jwt_identity()
    return respond(data=User.get_by_id(user).to_dict())

@bp.route('/api/v1/users/me/affiliate', methods=['GET'])
def affiliate_user_v1(user_id: int):
    pass

@bp.route('/api/v1/users/register', methods=['POST'])
def register_user_v1():
    login = request.json['login']
    email = request.json['email']
    password = request.json['password']

    if User.get_by_login(login):
        return respond(error="bad_request", detail={"login": "Login already taken"}), 400

    if User.get_by_email(email):
        return respond(error="bad_request", detail={"email": "Email already taken"}), 400

    if not User.validate_login(login):
        return respond(error="bad_request", detail={"login": "Invalid login"}), 400

    if not User.validate_email(email):
        return respond(error="bad_request", detail={"email": "Invalid email"}), 400

    if not User.validate_password(password):
        return respond(error="bad_request", detail={"password": "Invalid password"}), 400

    send_registration_verification_mail(login, email, password)

    return jsonify(
        data={
            "msg": "Email sent",
        }
    ), 200

@bp.route("/api/v1/users/verify", methods=["POST"])
def verify_registration_v1():
    if "token" not in request.json:
        return respond(error="bad_request", detail={"token": "Token missing"}), 400

    token = request.json["token"]

    user_info = User.verify_registration_token(token)
    if user_info is None:
        return respond(error="bad_request", detail={"token": "Invalid token"}), 400

    login = user_info["login"]
    email = user_info["email"]
    password = user_info["password"]

    if User.get_by_login(login) or User.get_by_email(email):
        return respond(error="bad_request", detail={"token": "Token already used"}), 400

    user = User(login=login, email=email, password=password)
    user.add()

    return respond(data={
        "access_token": create_access_token(identity=user.id),
        "refresh_token": create_refresh_token(identity=user.id)
    })


@bp.route('/api/v1/users/login', methods=['POST'])
def login_user_v1():
    login = request.json['login']
    password = request.json['password']

    user = User.get_by_login(login)
    if not user:
        return respond(error="not_found", detail={"user": "User does not exist"}), 404

    if not user.check_password(password):
        return respond(error="bad_request", detail={"password": "Incorrect password"}), 400

    return respond(data={
        "access_token": create_access_token(identity=user.id),
        "refresh_token": create_refresh_token(identity=user.id)
    })


@bp.route("/api/v1/users/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_user_v1():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return respond(data={
        "access_token": access_token,
        "refresh_token":refresh_token
    })


@bp.route("/api/v1/users/forgot", methods=["POST"])
def forgot_user_v1():
    if "email" not in request.json:
        return respond(error="bad_request", detail={"email": "Email missing"}), 400

    email = request.json["email"]

    user = User.get_by_email(email)

    if user is None:
        return respond(error="not_found", detail={"user": "User does not exist"}), 404

    send_password_recovery_mail(user.id, email)

    return jsonify(
        msg="Email sent",
    )


@bp.route("/api/v1/users/recovery", methods=["POST"])
def recover_user_v1():
    if "token" not in request.json:
        return respond(error="bad_request", detail={"token": "Token missing"}), 400

    if "password" not in request.json:
        return respond(error="bad_request", detail={"password": "Password missing"}), 400

    token = request.json["token"]
    password = request.json["password"]

    user = User.verify_recovery_token(token)

    if user is None:
        return respond(error="bad_request", detail={"token": "Invalid token"}), 400

    if not User.validate_password(password):
        return respond(error="bad_request", detail={"password": "Invalid password"}), 400

    user.set_password(password)
    user.update()

    return respond(data={"msg":"Password updated"})