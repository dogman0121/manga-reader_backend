from sqlalchemy import ForeignKey

from app import db

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

from app.logs import app_logger


class List(db.Model):
    __tablename__ = 'list'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    private: Mapped[bool] = mapped_column(default=True)

    manga: Mapped[list["Manga"]] = relationship("Manga", uselist=True,
                                                secondary="list_manga",
                                                )
    creator: Mapped["User"] = relationship("User", uselist=True, back_populates="lists")

    @hybrid_property
    def saves_count(self) -> int:
        return List.query.join(ListSave).filter_by(list_id=self.id).count()

    def is_saved_by_user(self, user) -> bool:
        return ListSave.query.filter_by(list_id=self.id, creator_id=user.id).count() > 0

    def add_manga(self, manga):
        new_list_manga = ListManga(list_id=self.id, manga_id=manga.id)
        db.session.add(new_list_manga)

    def remove_manga(self, manga):
        list_manga = ListManga.query.filter_by(list_id=self.id, manga_id=manga.id).first()
        db.session.delete(list_manga)

    def add_save(self, user):
        save = ListSave(list_id=self.id, user_id=user.id)
        db.session.add(save)

    def remove_save(self, user):
        save = ListSave.query.filter_by(list_id=self.id, user_id=user.id).first()
        db.session.delete(save)

    def to_dict(self, user=None, with_manga=False, with_creator=False):
        app_logger.info([i.main_poster for i in self.manga[:4]])
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "saves_count": self.saves_count,
            "preview": [
                i.main_poster.get_size("small").get_url() for i in self.manga[:4]
            ]
        }

        if with_manga:
            data["manga"] = [i.to_dict() for i in self.manga]

        if with_creator:
            data["creator"] = self.creator.to_dict()

        if user:
            data["is_saved_by_user"] = self.is_saved_by_user

        return data

class ListManga(db.Model):
    __tablename__ = 'list_manga'

    list_id: Mapped[int] = mapped_column(ForeignKey("list.id"), primary_key=True)
    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id"), primary_key=True)


class ListSave(db.Model):
    __tablename__ = 'list_save'

    list_id: Mapped[int] = mapped_column(ForeignKey("list.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)