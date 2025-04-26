from flask_jwt_extended import JWTManager
from app.utils import respond

jwt = JWTManager()

@jwt.expired_token_loader
def expired_token_callback():
    return respond(error="unauthorized", detail={"token": "expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback():
    return respond(error="unauthorized", detail={"token": "invalid"}), 401