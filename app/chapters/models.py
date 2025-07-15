from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app import storage, db
from app.models import Base, File

from datetime import datetime

class Page(Base, File):
    __tablename__ = "page"

    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapter.id"), nullable=True)
    order: Mapped[int] = mapped_column(nullable=False)

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "filename": self.uuid + self.ext,
            "link": storage.get_url(f"chapter/{self.chapter_id}/{self.uuid}{self.ext}"),
            "order": self.order,
        }

class Chapter(Base):
    __tablename__ = "chapter"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    tome: Mapped[int] = mapped_column(nullable=True)
    chapter: Mapped[int] = mapped_column(nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    translation_id: Mapped[int] = mapped_column(ForeignKey("translation.id"), nullable=True)

    pages: Mapped[list["Page"]] = relationship()
    translation: Mapped["Translation"] = relationship(back_populates="chapters")
    creator: Mapped["User"] = relationship()

    @staticmethod
    def get_by_chapter_number(translation_id, chapter_number):
        return Chapter.query.filter_by(translation_id=translation_id, chapter=chapter_number).first()

    @hybrid_property
    def next(self):
        return (
            db.session.query(Chapter)
            .filter_by(chapter=self.chapter+1, translation_id=self.translation_id)
            .first()
        )

    @hybrid_property
    def previous(self):
        return (
            db.session.query(Chapter)
            .filter_by(chapter=self.chapter - 1, translation_id=self.translation_id)
            .first()
        )

    def to_dict(self, previous=False, next=False):
        return {
            "id": self.id,
            "name": self.name,
            "tome": self.tome,
            "chapter": self.chapter,
            "creator": self.creator.to_dict() if self.creator else None,
            "pages": [i.to_dict() for i in self.pages],
            "next_chapter": self.next.to_dict() if self.next and next else None,
            "previous_chapter": self.previous.to_dict() if self.previous and previous else None,
        }
