from typing import List, Optional

from sqlalchemy import func

from app.domain.entities.manga.genre import Genre
from app.domain.entities.manga.manga import Manga
from app.domain.repositories.manga_repo import MangaRepository

from app.infrastructure.models.manga.sql_manga import SQLManga

class SQLMangaRepository(MangaRepository):
    @staticmethod
    def _to_entity(model: SQLManga) -> Manga:
        genres = [
            Genre(id=g.id,name=g.name)
            for g in model.genres
        ]

        return Manga(
            id=model.id,
            name=model.name,
            slug=model.slug,
            views=model.views,
            genres=genres,
            verified=model.verified,
        )

    def get_by_id(self, manga_id: int) -> Optional[Manga]:
        res = SQLManga.query.filter_by(id=manga_id).first()
        return self._to_entity(res) if res else None

    def get_by_slug(self, slug: str) -> Optional[Manga]:
        res = SQLManga.query.filter_by(slug=slug).first()
        return self._to_entity(res) if res else None

    def get_newest(self, verified: bool = None) -> List[Manga]:
        query = SQLManga.query

        if verified is not None:
            query = query.filter_by(verified=True)

        res = query.order_by(SQLManga.created_at.desc()).all()

        return [self._to_entity(m) for m in res]

    def get_ended(self, verified: bool = None) -> List[Manga]:
        query = SQLManga.query

        if verified is not None:
            query = query.filter_by(verified=verified)

        res = query.filter_by(status_id=4).all()

        return [self._to_entity(m) for m in res]

    def get_most_viewed(self, verified: bool = None) -> List[Manga]:
        query = SQLManga.query

        if verified is not None:
            query = query.filter_by(verified=verified)

        res = query.order_by(SQLManga.views.desc()).all()

        return [self._to_entity(m) for m in res]

    def get_random(self, verified: bool = None) -> List[Manga]:
        query = SQLManga.query

        if verified is not None:
            query = query.filter_by(verified=verified)

        res = query.order_by(func.random).first()

        return [self._to_entity(m) for m in res]