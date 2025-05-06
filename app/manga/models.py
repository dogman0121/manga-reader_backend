import os

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from app import db
from app.models import Base
from datetime import datetime
from sqlalchemy import Integer, Text, ForeignKey, DateTime, Column, Table, String, Select, func, desc, and_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.manga.utils import get_external_path

from typing import Optional

manga_authors = Table(
    "manga_author",
    db.metadata,
    Column("manga_id", Integer, db.ForeignKey("manga.id")),
    Column("person_id", Integer, db.ForeignKey("person.id")),
)

manga_artists = Table(
    "manga_artist",
    db.metadata,
    Column("manga_id", Integer, db.ForeignKey("manga.id")),
    Column("person_id", Integer, db.ForeignKey("person.id")),
)

manga_publishers = Table(
    "manga_publisher",
    db.metadata,
    Column("manga_id", Integer, db.ForeignKey("manga.id")),
    Column("person_id", Integer, db.ForeignKey("person.id")),
)

manga_genres = Table(
    "manga_genre",
    db.metadata,
    Column("genre_id", Integer, db.ForeignKey("genre.id")),
    Column("title_id", Integer, db.ForeignKey("manga.id")),
)

class Rating(Base):
    __tablename__ = "rating"

    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id"), primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True, nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)

    @staticmethod
    def get(user_id: int, manga_id: int) -> Optional["Rating"]:
        return db.session.execute(
            Select(Rating).where(and_(Rating.manga_id == manga_id, Rating.user_id == user_id))
        ).scalar()

class Genre(Base):
    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }

class Type(Base):
    __tablename__ = "type"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }

class Status(Base):
    __tablename__ = "status"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }


class Adult(Base):
    __tablename__ = "adult"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }

class NameTranslation(Base):
    __tablename__ = "manga_name_translation"

    manga_id: Mapped[int] = mapped_column(Integer, ForeignKey("manga.id"), primary_key=True,
                                          nullable=False)
    lang: Mapped[str] = mapped_column(String(5), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    def to_dict(self):
        return {
            "lang": self.lang,
            "name": self.name,
        }

class Poster(Base):
    __tablename__ = "manga_poster"

    uuid: Mapped[str] = mapped_column(primary_key=True)
    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    filenames: Mapped[str] = mapped_column(JSONB, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    manga = relationship("Manga", backref="posters")


def get_poster_dict(manga_id: int, poster: Poster) -> dict:

    return {
        "uuid": poster.uuid,
        "thumbnail": f"/uploads/manga/{manga_id}/{poster.filenames['thumbnail']}",
        "small": f"/uploads/manga/{manga_id}/{poster.filenames['small']}",
        "medium": f"/uploads/manga/{manga_id}/{poster.filenames['medium']}",
        "large": f"/uploads/manga/{manga_id}/{poster.filenames['large']}",
    }

class Save(Base):
    __tablename__ = "save"

    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

class Manga(Base):
    page_size = 20

    __tablename__ = 'manga'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    name_translations: Mapped[list["NameTranslation"]] = relationship(cascade="save-update, merge, delete, delete-orphan")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("type.id"), nullable=True)
    type: Mapped["Type"] = relationship()
    status_id: Mapped[Optional[int]] = mapped_column(ForeignKey("status.id"), nullable=True)
    status: Mapped["Status"] = relationship()
    main_poster_number: Mapped[Optional[int]] = mapped_column(nullable=True)
    main_poster: Mapped["Poster"] = relationship("Poster",
        primaryjoin="and_(Manga.main_poster_number == Poster.order, Manga.id == Poster.manga_id)",
    )
    posters: Mapped[list["Poster"]] = relationship("Poster",
                                                   cascade="save-update, merge, delete, delete-orphan",
                                                   back_populates="manga")
    background: Mapped[str] = mapped_column(nullable=True)
    year: Mapped[Optional[int]] = mapped_column(nullable=True)
    views: Mapped[Optional[int]] = mapped_column(default=0)
    adult_id: Mapped[Optional[int]] = mapped_column(ForeignKey("adult.id"), nullable=True)
    adult: Mapped["Adult"] = relationship()
    genres: Mapped[list["Genre"]] = relationship("Genre", secondary="manga_genre")
    authors: Mapped[list["Person"]] = relationship(secondary="manga_author")
    artists: Mapped[list["Person"]] = relationship(secondary="manga_artist")
    publishers: Mapped[list["Person"]] = relationship(secondary="manga_publisher")
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    creator: Mapped["User"] = relationship("User")
    # chapters: Mapped[list["Chapter"]] = relationship(uselist=True, back_populates="manga")
    # translators: Mapped[list["Team"]] = relationship(uselist=True, secondary="manga_translator",
    #                                                  back_populates="mangas")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda x: datetime.utcnow(), nullable=True)
    verified: Mapped[bool] = mapped_column(default=False)
    comments: Mapped["Comment"] = relationship("Comment", secondary="manga_comment", back_populates="manga")

    @staticmethod
    def get(manga_id):
        return db.session.get(Manga, manga_id)

    @hybrid_property
    def rating(self):
        response = db.session.execute(
            Select(func.sum(Rating.rating), func.count(Rating.rating))
            .where(Rating.manga_id == self.id)
        ).one()

        if response[0] is None or response[1] is None:
            return [0, 0, 0]

        ratings_sum, ratings_count = response
        return round(ratings_sum / ratings_count, 2), ratings_sum, ratings_count

    @hybrid_property
    def saves_count(self):
        return db.session.execute(Select(func.count(Save.manga_id)).where(Save.manga_id == self.id)).scalar()

    # ----- Filters -----
    @hybrid_method
    def validate_types(self, type_ids: list[int]):
        if not type_ids:
            return True

        return self.type_id.in_(type_ids)

    @hybrid_method
    def validate_statuses(self, status_ids: list[int]):
        if not status_ids:
            return True

        return self.status.id in status_ids

    @hybrid_method
    def validate_genres(self, genres: list[int]):
        if not genres:
            return True

        if not self.genres:
            return False

        return Manga.genres.any(Genre.id.in_(genres))

    @hybrid_method
    def validate_year(self, year_from: int, year_to: int):
        return and_(year_from <= self.year, self.year <= year_to)

    @hybrid_method
    def validate_rating(self, rating_from: int, rating_to: int):
        rating_sum, rating_len = self.rating
        if rating_len == 0:
            return True if rating_from == 0 else False
        rating = rating_sum / rating_len
        return and_(rating_from <= rating, rating <= rating_to)

    @staticmethod
    def get_with_filters(types: list[int] = (), statuses: list[int] = (), genres: list[int] = (),
                         year_from: int = 0, year_to: int = 10000, rating_from: int = 0, rating_to: int = 10,
                         adult: bool = False, sortings: int = 1, page: int = 1):
        query = (Select(Manga).filter(
            Manga.validate_types(types),
            Manga.validate_statuses(statuses),
            Manga.validate_year(year_from, year_to),
            Manga.validate_genres(genres),
            Manga.validate_rating(rating_from, rating_to)
        )
            .join(Save, Save.manga_id == Manga.id, isouter=True)
            .join(Rating, Rating.manga_id == Manga.id, isouter=True)
            .group_by(Manga.id))

        if sortings == 1:
            return db.session.execute(query.order_by(desc(Manga.views)).limit(Manga.page_size).offset(Manga.page_size * (page-1))).scalars().all()
        elif sortings == 2:
            return db.session.execute(query.order_by(desc(func.count(Save.manga_id))).limit(Manga.page_size).offset(Manga.page_size * (page-1))).scalars().all()
        elif sortings == 3:
            return db.session.execute(query.order_by(desc(func.count(Rating.manga_id))).limit(Manga.page_size).offset(Manga.page_size * (page-1))).scalars().all()
        elif sortings == 4:
            return db.session.execute(query.order_by(desc(Manga.year)).limit(Manga.page_size).offset(Manga.page_size * (page-1))).scalars().all()

    @staticmethod
    def search(query, page=1):
        return db.session.execute(
            Select(Manga)
            .filter(func.lower(Manga.name).like(f"%{query.lower()}%"))
            .limit(Manga.page_size).offset(Manga.page_size * (page-1))
        ).scalars().all()

    def can_edit(self, user):
        if user is None:
            return False

        if self.creator == user:
            return True

        if user.role == 4:
            return True

        return False

    def get_permissions(self, user):
        if user is None:
            return {}

        return {
            "edit": self.can_edit(user),
        }

    def add_rating(self, user, rating):
        rating = Rating(user_id=user.id, manga_id=self.id, rating=rating)
        rating.add()

    def update_rating(self, user, new_rating):
        rating = Rating.get(user_id=user.id, manga_id=self.id)
        rating.rating = new_rating
        rating.update()

    def delete_rating(self, user):
        rating = Rating.get(user_id=user.id, manga_id=self.id)

        if rating is not None:
            rating.delete()

    def to_dict(self, user=None, posters=False):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.to_dict() if self.type else None,
            "status": self.status.to_dict() if self.status else None,
            "adult": self.adult.to_dict() if self.adult else None,
            "year": self.year if self.year else None,
            "views": self.views,
            "rating": self.rating[0],
            "saves": self.saves_count,
            "rating_count": self.rating[2],
            "name_translations": [i.to_dict() for i in self.name_translations],
            "main_poster":
                get_poster_dict(self.id, self.main_poster)
                if self.main_poster else None,
            "background":
                f"/uploads/manga/{self.id}/{self.background}"
                if self.background else None,
            "posters": [
                get_poster_dict(self.id, poster) for poster in sorted(self.posters, key=lambda x: x.order)
            ] if posters else [],
            "authors": [author.to_dict() for author in self.authors],
            "artists": [artist.to_dict() for artist in self.artists],
            "publishers": [publisher.to_dict() for publisher in self.publishers],
            "permissions": self.get_permissions(user),
            "description": self.description,
            "genres": [i.to_dict() for i in self.genres],
            "user_rating": Rating.get(user.id, self.id).rating if user and Rating.get(user.id, self.id) else None,
        }

