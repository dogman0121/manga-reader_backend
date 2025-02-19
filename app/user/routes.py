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


@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    return jsonify(User.get_by_id(user_id))

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def edit_user(user_id: int):
    user = User.get_by_id(int(get_jwt_identity()))

    if user.id != user_id:
        return jsonify(msg="You are not allowed to edit this user"), 403

    if "login" in request.json:
        user.login = request.json["login"]

    if "password" in request.json:
        user.password = request.json["password"]

    user.update()
    return jsonify(user.to_dict())

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user = get_jwt_identity()
    return jsonify(User.get_by_id(user).to_dict())


@bp.route('/register', methods=['POST'])
def register_user():
    login = request.json['login']
    email = request.json['email']
    password = request.json['password']

    if User.get_by_login(login):
        return jsonify({"msg": "Login already taken"})

    if User.get_by_email(email):
        return jsonify({"msg": "Email already taken"})

    send_registration_verification_mail(login, email, password)

    return jsonify(
        msg="Email sent",
    )

@bp.route("/verify", methods=["POST"])
def verify_registration():
    if "token" not in request.json:
        return jsonify({"msg": "Token missing"})

    token = request.json["token"]

    user_info = User.verify_registration_token(token)

    if user_info is None:
        return jsonify({"msg": "Invalid token"})

    user = User(login=user_info["login"], email=user_info["email"], password=user_info["password"])
    user.add()

    return jsonify(
        access_token=create_access_token(identity=user.id),
        refresh_token=create_refresh_token(identity=user.id),
    )


@bp.route('/login', methods=['POST'])
def login_user():
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


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_user():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return jsonify(access_token=access_token, refresh_token=refresh_token)

@bp.route("/forgot", methods=["POST"])
def forgot_user():
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

@bp.route("/recovery", methods=["POST"])
def recover_user():
    if "token" not in request.json:
        return jsonify({"msg": "Token missing"})

    if "password" not in request.json:
        return jsonify({"msg": "Password missing"})

    token = request.json["token"]
    password = request.json["password"]

    user = User.verify_recovery_token(token)

    if user is None:
        return jsonify({"msg": "Invalid token"})

    user.set_password(password)
    user.update()

    return jsonify(
        access_token=create_access_token(identity=user.id),
        refresh_token=create_refresh_token(identity=user.id),
    )