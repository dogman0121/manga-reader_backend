import os

from sqlalchemy.ext.hybrid import hybrid_property

from flask import url_for

from app import db
from app.models import Base
from datetime import datetime
from sqlalchemy import Integer, Text, ForeignKey, DateTime, Column, Table, String, Select, func
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

class Genre(Base):
    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

class Type(Base):
    __tablename__ = "type"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

class Status(Base):
    __tablename__ = "status"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)


class Adult(Base):
    __tablename__ = "adult"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

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

    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id"))
    filename: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

class Background(Base):
    __tablename__ = "manga_background"

    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id"))
    filename: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)

class Manga(Base):
    __tablename__ = 'manga'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    name_translations: Mapped[list["NameTranslation"]] = relationship()
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("type.id"), nullable=True)
    type: Mapped["Type"] = relationship()
    status_id: Mapped[Optional[int]] = mapped_column(ForeignKey("status.id"), nullable=True)
    status: Mapped["Status"] = relationship()
    main_poster_number: Mapped[Optional[int]] = mapped_column(nullable=True)
    main_poster: Mapped["Poster"] = relationship("Poster",
        primaryjoin="and_(Manga.main_poster_number == Poster.order, Manga.id == Poster.manga_id)",
    )
    posters: Mapped[list["Poster"]] = relationship()
    background: Mapped["Background"] = relationship()
    year: Mapped[Optional[int]] = mapped_column(nullable=True)
    views: Mapped[Optional[int]] = mapped_column(default=0)
    adult_id: Mapped[Optional[int]] = mapped_column(ForeignKey("adult.id"), nullable=True)
    adult: Mapped["Adult"] = relationship()
    genres: Mapped[list["Genre"]] = relationship(secondary="manga_genre")
    authors: Mapped[list["Person"]] = relationship(secondary="manga_author")
    artists: Mapped[list["Person"]] = relationship(secondary="manga_artist")
    publishers: Mapped[list["Person"]] = relationship(secondary="manga_publisher")
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    creator: Mapped["User"] = relationship("User")
    # chapters: Mapped[list["Chapter"]] = relationship(uselist=True, back_populates="manga")
    # translators: Mapped[list["Team"]] = relationship(uselist=True, secondary="manga_translator",
    #                                                  back_populates="mangas")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda x: datetime.utcnow())
    verified: Mapped[bool] = mapped_column(default=False)

    @staticmethod
    def get(manga_id):
        return db.session.get(Manga, manga_id)

    @staticmethod
    def search(query):
        return db.session.execute(
            Select(Manga).filter(func.lower(Manga.name).like(f"%{query.lower()}%"))
        ).scalars().all()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "name_translations": [i.to_dict() for i in self.name_translations],
            "main_poster":
                get_external_path(f"/uploads/manga/{self.id}/{self.main_poster.filename}")
                if self.main_poster_number else "",
            "background":
                get_external_path(f"/uploads/manga/{self.id}/{self.background.filename}")
                if self.background else "",
            "posters": [
                get_external_path(f"/uploads/manga/{self.id}/{poster.filename}") for poster in self.posters
            ],
        }

