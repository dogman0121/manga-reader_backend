from app import db
from app.models import Base
from datetime import datetime
from sqlalchemy import Integer, Text, ForeignKey, DateTime, Column, Table, String, Select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


manga_name_translations = Table(
    "manga_name_translation",
    db.metadata,
    Column("manga_id", Integer, db.ForeignKey("manga.id")),
    Column("lang", String(5), nullable=False),
    Column("name", Text, nullable=False),
)

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

class Type(Base):
    __tablename__ = "type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

class Status(Base):
    __tablename__ = "status"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

class NameTranslation(Base):
    __tablename__ = "name_translation"

    manga_id: Mapped[int] = mapped_column(Integer, ForeignKey("manga.id"), primary_key=True,
                                          nullable=False)
    lang: Mapped[str] = mapped_column(String(5), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)

class Manga(Base):
    __tablename__ = 'manga'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    name_translations: Mapped[list["NameTranslation"]] = relationship()
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("type.id"), nullable=True)
    type: Mapped["Type"] = relationship()
    status_id: Mapped[int] = mapped_column(ForeignKey("status.id"), nullable=True)
    status: Mapped["Status"] = relationship()
    poster: Mapped[int] = mapped_column(nullable=True)
    year: Mapped[int] = mapped_column(nullable=True)
    views: Mapped[int] = mapped_column(default=0)
    adult: Mapped[int] = mapped_column()
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

    @staticmethod
    def get(manga_id):
        return db.session.get(Manga, manga_id)

    @staticmethod
    def search(query):
        return db.session.execute(
            Select(Manga).filter(func.lower(Manga.name).like(f"%{query.lower()}%"))
        ).scalars().all()

