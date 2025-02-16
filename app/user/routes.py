from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required

)
from app.user import bp
from app.user.models import User


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

    user = User(login=login, email=email, password=password)
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