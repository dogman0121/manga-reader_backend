from flask_jwt_extended import JWTManager
from app.utils import respond

jwt = JWTManager()

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return respond(error="unauthorized", detail={"token": "Token expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return respond(error="unauthorized", detail={"token": "Invalid token"}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return respond(error="unauthorized", detail={"token": "Missing authorization token"}), 401

