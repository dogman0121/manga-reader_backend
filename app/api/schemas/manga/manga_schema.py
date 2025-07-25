from marshmallow import fields, Schema

from app.user.schemas import UserSchema


class MangaTypeSchema(Schema):
    id = fields.Integer()
    name = fields.String()

class MangaStatusSchema(Schema):
    id = fields.Integer()
    name = fields.String()

class MangaAdultSchema(Schema):
    id = fields.Integer()
    name = fields.String()

class MangaPosterSchema(Schema):
    uuid = fields.UUID()
    thumbnail = fields.String()
    small = fields.String()
    medium = fields.String()
    orig = fields.String()
    order = fields.Integer()

class MangaPermissionsSchema(Schema):
    edit = fields.Boolean()
    delete = fields.Boolean()
    verify = fields.Boolean()

class MangaSchema(Schema):
    id = fields.Integer()
    slug = fields.String()
    name = fields.String()
    description = fields.String()
    type = fields.Nested(MangaTypeSchema)
    status = fields.Nested(MangaStatusSchema)
    adult = fields.Nested(MangaAdultSchema)
    main_poster_id = fields.Nested(MangaPosterSchema)
    background = fields.String()
    posters = fields.List(fields.Nested(MangaPosterSchema))
    authors = fields.List(fields.Nested(UserSchema))
    artists = fields.List(fields.Nested(UserSchema))
    publishers = fields.List(fields.Nested(UserSchema))
    verified = fields.Boolean()
    permissions = fields.Nested(MangaPermissionsSchema)