from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import storage
from app.models import Base, File

from datetime import datetime

class Page(Base, File):
    __tablename__ = "page"

    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapter.id"), nullable=True)
    order: Mapped[int] = mapped_column(nullable=False)

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "filename": self.uuid + "." + self.ext,
            "link": storage.get_url(f"/chapter/{self.chapter_id}/{self.uuid}.{self.ext}"),
            "order": self.order,
        }

class Chapter(Base):
    __tablename__ = "chapter"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    tome: Mapped[int] = mapped_column(nullable=True)
    chapter: Mapped[int] = mapped_column(nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    pages: Mapped[list["Page"]] = relationship()
    team: Mapped["Team"] = relationship()
    creator: Mapped["User"] = relationship()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tome": self.tome,
            "chapter": self.chapter,
            "team": self.team.to_dict() if self.team else None,
            "creator": self.creator.to_dict() if self.creator else None,
            "pages": [i.to_dict() for i in self.pages]
        }
