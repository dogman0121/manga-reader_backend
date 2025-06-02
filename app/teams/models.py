from sqlalchemy import ForeignKey

from app import storage
from app.models import Base, File
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class TeamMember(Base):
    __tablename__ = 'team_member'

    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

class TeamPoster(Base, File):
    __tablename__ = 'team_poster'

    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), primary_key=True)

class Team(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    about: Mapped[str] = mapped_column(nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=True, default=lambda x: datetime.utcnow())

    members: Mapped[list[TeamMember]] = relationship(backref="team", uselist=True)
    poster: Mapped["TeamPoster"] = relationship()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "about": self.about,
            "poster": storage.get(f"/team/{self.id}/{self.poster.uuid}.{self.poster.ext}", ) if self.poster else None,
        }