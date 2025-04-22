from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required
)
from app.user import bp
from app.user.models import User
from app.email import send_registration_verification_mail, send_password_recovery_mail


@bp.route('/api/v1/users/<int:user_id>', methods=['GET'])
@jwt_required(optional=True)
def get_user_v1(user_id: int):
    user = User.get_by_id(user_id)
    current_user = User.get_by_id(get_jwt_identity())

    if user is None:
        return jsonify(data=None, error={"code": "not_found"}), 404
    return jsonify(data = user.to_dict(user=current_user)), 200

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
        return jsonify(error=None, data=None), 204
    elif request.method == 'DELETE':
        user.unsubscribe(subscriber)
        return jsonify(error=None, data=None), 204


@bp.route('/api/v1/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def edit_user_v1(user_id: int):
    user = User.get_by_id(int(get_jwt_identity()))

    if user.id != user_id:
        return jsonify(msg="You are not allowed to edit this user"), 403

    if "login" in request.json:
        user.login = request.json["login"]

    if "password" in request.json:
        user.password = request.json["password"]

    user.update()
    return jsonify(user.to_dict())

@bp.route('/api/v1/users/me', methods=['GET'])
@jwt_required()
def get_current_user_v1():
    user = get_jwt_identity()
    return jsonify(data=User.get_by_id(user).to_dict())


@bp.route('/api/v1/users/register', methods=['POST'])
def register_user_v1():
    login = request.json['login']
    email = request.json['email']
    password = request.json['password']

    if User.get_by_login(login):
        return jsonify({"msg": "Login already taken"})

    if User.get_by_email(email):
        return jsonify({"msg": "Email already taken"})

    if not User.validate_login(login):
        return jsonify({"msg": "Invalid login"})

    if not User.validate_email(email):
        return jsonify({"msg": "Invalid email"})

    if not User.validate_password(password):
        return jsonify({"msg": "Invalid password"})

    send_registration_verification_mail(login, email, password)

    return jsonify(
        msg="Email sent",
    )

@bp.route("/api/v1/users/verify", methods=["POST"])
def verify_registration_v1():
    if "token" not in request.json:
        return jsonify({"msg": "Token missing"})

    token = request.json["token"]

    user_info = User.verify_registration_token(token)
    if user_info is None:
        return jsonify({"msg": "Invalid token"})

    login = user_info["login"]
    email = user_info["email"]
    password = user_info["password"]

    if User.get_by_login(login) or User.get_by_email(email):
        return jsonify({"msg": "Token already used"})

    user = User(login=login, email=email, password=password)
    user.add()

    return jsonify(
        access_token=create_access_token(identity=user.id),
        refresh_token=create_refresh_token(identity=user.id),
    )


@bp.route('/api/v1/users/login', methods=['POST'])
def login_user_v1():
    login = request.json['login']
    password = request.json['password']

    user = User.get_by_login(login)
    if not user:
        return jsonify({"msg": "User does not exist"})

    if not user.check_password(password):
        return jsonify({"msg": "Incorrect password"})

    return jsonify(
        access_token=create_access_token(identity=user.id),
        refresh_token=create_refresh_token(identity=user.id),
    )


@bp.route("/api/v1/users/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_user_v1():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@bp.route("/api/v1/users/forgot", methods=["POST"])
def forgot_user_v1():
    if "email" not in request.json:
        return jsonify({"msg": "Email missing"})

    email = request.json["email"]

    user = User.get_by_email(email)

    if user is None:
        return jsonify({"msg": "User does not exist"})

    send_password_recovery_mail(user.id, email)

    return jsonify(
        msg="Email sent",
    )


@bp.route("/api/v1/users/recovery", methods=["POST"])
def recover_user_v1():
    if "token" not in request.json:
        return jsonify({"msg": "Token missing"})

    if "password" not in request.json:
        return jsonify({"msg": "Password missing"})

    token = request.json["token"]
    password = request.json["password"]

    user = User.verify_recovery_token(token)

    if user is None:
        return jsonify({"msg": "Invalid token"})

    if not User.validate_password(password):
        return jsonify({"msg": "Invalid password"})

    user.set_password(password)
    user.update()

    return jsonify(msg="Password updated")