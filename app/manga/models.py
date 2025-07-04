import os

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from typing_extensions import override

from app import db, storage
from app.models import Base, File
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
    Column("user_id", Integer, db.ForeignKey("user.id")),
)

manga_artists = Table(
    "manga_artist",
    db.metadata,
    Column("manga_id", Integer, db.ForeignKey("manga.id")),
    Column("user_id", Integer, db.ForeignKey("user.id")),
)

manga_publishers = Table(
    "manga_publisher",
    db.metadata,
    Column("manga_id", Integer, db.ForeignKey("manga.id")),
    Column("user_id", Integer, db.ForeignKey("user.id")),
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

class PosterFile(Base, File):
    __tablename__ = "manga_poster_file"
    uuid: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=True)
    poster_uuid: Mapped[str] = mapped_column(ForeignKey("manga_poster.uuid"), nullable=False)

    poster: Mapped["Poster"] = relationship("Poster", back_populates="files")

class Poster(Base):
    __tablename__ = "manga_poster"

    uuid: Mapped[str] = mapped_column(primary_key=True)
    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    manga: Mapped["Manga"] = relationship(back_populates="posters")
    files: Mapped[list["PosterFile"]] = relationship(uselist=True, back_populates="poster")

    def to_dict(self):
        dct =  dict(
            [(file.type, storage.get_url(f"manga/{self.manga_id}/{file.uuid}{file.ext}")) for file in self.files]
        )
        dct["uuid"] = self.uuid

        return dct

    def add_file(self, file: PosterFile):
        self.files.append(file)

    @override
    def delete(self):
        for file in self.files:
            storage.delete(f"manga/${self.manga_id}/${file.uuid}{file.ext}")
            file.delete()
        self.delete()


class Save(Base):
    __tablename__ = "save"

    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

class Translation(Base):
    __tablename__ = "translation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)

    chapters: Mapped[list["Chapter"]] = relationship(uselist=True, lazy="dynamic", back_populates="translation")
    team: Mapped["Team"] = relationship("Team")
    user: Mapped["User"] = relationship("User")

    @hybrid_property
    def chapters_count(self):
        return self.chapters.count()

    def get_permissions(self, user):
        if user is None:
            return {}
        else:
            if user.id == self.user_id:
                return {
                    "update": True,
                    "delete": True,
                    "add_chapters": True
                }

        return {}

    def to_dict(self, user=None) -> dict:
        return {
            "id": self.id,
            "translator_type": "team" if self.team_id else "user",
            "translator": self.team.to_dict() if self.team_id else self.user.to_dict(),
            "chapters_count": self.chapters_count,
            "permissions": self.get_permissions(user)
        }

    @staticmethod
    def get_by_team(manga_id, team_id):
        return Translation.query.filter_by(manga_id=manga_id, team_id=team_id).scalar()

    @staticmethod
    def get_by_user(manga_id, user_id):
        return Translation.query.filter_by(manga_id=manga_id, user_id=user_id).scalar()


class MangaService:
    @staticmethod
    def get_by_id(manga_id):
        return Manga.query.get(manga_id).scalar()

    @staticmethod
    def get_by_slug(slug):
        return Manga.query.filter_by(slug=slug).scalar()

class Manga(Base):
    page_size = 20

    __tablename__ = 'manga'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("type.id"), nullable=True)
    status_id: Mapped[Optional[int]] = mapped_column(ForeignKey("status.id"), nullable=True)
    main_poster_number: Mapped[Optional[int]] = mapped_column(nullable=True)
    background: Mapped[str] = mapped_column(nullable=True)
    year: Mapped[Optional[int]] = mapped_column(nullable=True)
    views: Mapped[Optional[int]] = mapped_column(default=0)
    adult_id: Mapped[Optional[int]] = mapped_column(ForeignKey("adult.id"), nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda x: datetime.utcnow(), nullable=True)
    verified: Mapped[bool] = mapped_column(default=False)

    name_translations: Mapped[list["NameTranslation"]] = relationship(
        cascade="save-update, merge, delete, delete-orphan")
    type: Mapped["Type"] = relationship()
    status: Mapped["Status"] = relationship()
    main_poster: Mapped["Poster"] = relationship(
        primaryjoin="and_(Manga.main_poster_number == Poster.order, Manga.id == Poster.manga_id)",
        back_populates="manga",
        uselist=False
    )
    posters: Mapped[list["Poster"]] = relationship(back_populates="manga")
    adult: Mapped["Adult"] = relationship()
    genres: Mapped[list["Genre"]] = relationship("Genre", secondary="manga_genre")
    authors: Mapped[list["User"]] = relationship(secondary="manga_author", uselist=True)
    artists: Mapped[list["User"]] = relationship(secondary="manga_artist", uselist=True)
    publishers: Mapped[list["User"]] = relationship(secondary="manga_publisher", uselist=True)
    creator: Mapped["User"] = relationship("User")
    # comments: Mapped["Comment"] = relationship("Comment", secondary="manga_comment", back_populates="manga")
    translations: Mapped[list["Translation"]] = relationship("Translation", uselist=True)

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

    @hybrid_property
    def main_poster(self):
        return (
            db.session.query(Poster)
            .filter(Poster.order == self.main_poster_number, Poster.manga_id == self.id).all()
        )

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

        return self.status_id.in_(status_ids)

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
        rating, rating_sum, rating_len = self.rating
        if rating_len == 0:
            return True if rating_from == 0 else False
        return and_(rating_from <= rating, rating <= rating_to)

    @staticmethod
    def get_with_filters(search="", types: list[int] = (), statuses: list[int] = (), genres: list[int] = (),
                         year_from: int = 0, year_to: int = 10000, rating_from: int = 0, rating_to: int = 10,
                         adult: bool = False, sortings: int = 1, page: int = 1, **kwargs):
        query = (Select(Manga).filter(
            Manga.validate_types(types),
            Manga.validate_statuses(statuses),
            Manga.validate_year(year_from, year_to),
            Manga.validate_genres(genres),
            Manga.validate_rating(rating_from, rating_to),
            func.lower(Manga.name).like(f"%{search}%")
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
            "slug": self.slug,
            "type": self.type.to_dict() if self.type else None,
            "status": self.status.to_dict() if self.status else None,
            "adult": self.adult.to_dict() if self.adult else None,
            "year": self.year if self.year else None,
            "views": self.views,
            "rating": self.rating[0],
            "saves": self.saves_count,
            "rating_count": self.rating[2],
            "name_translations": [i.to_dict() for i in self.name_translations],
            "main_poster": self.main_poster[0].to_dict() if self.main_poster else None,
            "background":
                storage.get_url(f"manga/{self.id}/{self.background}")
                if self.background else None,
            "posters": [p.to_dict() for p in self.posters],
            "authors": [author.to_dict() for author in self.authors],
            "artists": [artist.to_dict() for artist in self.artists],
            "publishers": [publisher.to_dict() for publisher in self.publishers],
            "permissions": self.get_permissions(user),
            "description": self.description,
            "genres": [i.to_dict() for i in self.genres],
            "user_rating": Rating.get(user.id, self.id).rating if user and Rating.get(user.id, self.id) else None,
            "translations": [i.to_dict(user=user) for i in self.translations],
        }

