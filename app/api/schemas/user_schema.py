from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Integer()
    avatar = fields.String()
    login = fields.String()
    email = fields.String()
    role = fields.Integer()
    created_at = fields.DateTime()