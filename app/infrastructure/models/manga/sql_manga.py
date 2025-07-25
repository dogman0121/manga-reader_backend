from typing import Optional, List

from datetime import datetime

from sqlalchemy import ForeignKey, Text, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import sqlalchemy_db
from app.infrastructure.database.models.base import SQLAlchemyBaseModel


class SQLAlchemyManga(sqlalchemy_db.Model, SQLAlchemyBaseModel):
    __tablename__ = 'manga'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
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


    name_translations: Mapped[List["NameTranslation"]] = relationship()
    type: Mapped["Type"] = relationship()
    status: Mapped["Status"] = relationship()
    posters: Mapped[List["Poster"]] = relationship(uselist=True, back_populates="manga")
    adult: Mapped["Adult"] = relationship()
    genres: Mapped[List["Genre"]] = relationship("Genre", secondary="manga_genre")
    authors: Mapped[List["User"]] = relationship(secondary="manga_author", uselist=True)
    artists: Mapped[List["User"]] = relationship(secondary="manga_artist", uselist=True)
    publishers: Mapped[List["User"]] = relationship(secondary="manga_publisher", uselist=True)
    creator: Mapped["User"] = relationship("User")
    translations: Mapped[List["Translation"]] = relationship("Translation", uselist=True, back_populates="manga")