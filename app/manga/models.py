from app import db

from datetime import datetime
from sqlalchemy import Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Manga(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("types.id"), nullable=True)
    type: Mapped["Type"] = relationship()
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"), nullable=True)
    status: Mapped["Status"] = relationship()
    description: Mapped[str] = mapped_column(nullable=True)
    poster: Mapped[int] = mapped_column(nullable=True)
    year: Mapped[int] = mapped_column(nullable=True)
    views: Mapped[int] = mapped_column(default=0)
    genres: Mapped[list["Genre"]] = relationship(secondary="titles_genres")
    author: Mapped[list["Person"]] = relationship(secondary="titles_authors")
    artist: Mapped[list["Person"]] = relationship(secondary="titles_artists")
    publisher: Mapped[list["Person"]] = relationship(secondary="titles_publishers")
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    creator: Mapped["User"] = relationship("User")
    chapters: Mapped[list["Chapter"]] = relationship(uselist=True, back_populates="title")
    translators: Mapped[list["Team"]] = relationship(uselist=True, secondary="titles_translators",
                                                     back_populates="titles")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda x: datetime.utcnow())