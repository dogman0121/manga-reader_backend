from marshmallow import fields, Schema

from app.api.schemas.manga.manga_name_translations_schema import MangaNameTranslationsSchema
from app.api.schemas.user_schema import UserSchema


class MangaCreateSchema(Schema):
    name = fields.String(required=True)
    name_translations = fields.List(fields.Nested(MangaNameTranslationsSchema), required=False)
    description = fields.String(required=False)
    status = fields.Integer(required=False)
    type = fields.Integer(required=False)
    adult = fields.Integer(required=False)
    genres = fields.Integer(required=False)
    year = fields.Integer(required=False)
    main_poster = fields.Integer(required=False)
    authors = fields.List(fields.Integer, required=False)
    artists = fields.List(fields.Integer, required=False)
    publishers = fields.List(fields.Integer, required=False)