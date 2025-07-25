from marshmallow import Schema, fields

from .manga.manga_schema import MangaSchema


class HomeSchema(Schema):
    slides = fields.List(fields.Nested(MangaSchema))
    ended = fields.List(fields.Nested(MangaSchema))
    newest = fields.List(fields.Nested(MangaSchema))
    last_updates = fields.List(fields.Nested(MangaSchema))