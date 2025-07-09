from sqlalchemy import ForeignKey

from app import db

from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class ListService:
    def __init__(self):
        pass

    @staticmethod
    def get_list(list_id):
        return List.query.get(list_id)

class List(db.Model):
    __tablename__ = 'list'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    private: Mapped[bool] = mapped_column(default=True)

    manga: Mapped[list["Manga"]] = relationship("Manga", uselist=True,
                                                secondary="list_manga",
                                                )
    creator: Mapped["User"] = relationship("User", uselist=True, back_populates="lists")

    def add_manga(self, title):
        new_list_title = ListTitle(list_id=self.id, title_id=title.id)
        db.session.add(new_list_title)

    def remove_manga(self, title):
        list_title = ListTitle.query.filter_by(list_id=self.id, title_id=title.id).first()
        db.session.delete(list_title)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "creator_id": self.creator.to_dict(),
            "created_at": self.created_at,
        }

class ListTitle(db.Model):
    __tablename__ = 'list_manga'

    list_id: Mapped[int] = mapped_column(ForeignKey("manga.id"), primary_key=True)
    manga_id: Mapped[int] = mapped_column(ForeignKey("list.id"), primary_key=True)
