from PIL.ImageChops import offset
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

from app import db
from app.models import Base


class Notification(Base):
    page_size = 10

    __tablename__ = "notification"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('team.id'), nullable=True)
    # post_id: Mapped[int] = mapped_column(ForeignKey('post.id'))
    chapter_id: Mapped[int] = mapped_column(ForeignKey('chapter.id'), nullable=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey('comment.id'), nullable=True)
    manga_id: Mapped[int] = mapped_column(ForeignKey('manga.id'), nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="notifications", foreign_keys=[user_id])
    chapter: Mapped["Chapter"] = relationship()
    actor: Mapped["User"] = relationship(foreign_keys=[actor_id])
    team: Mapped["Team"] = relationship()
    comment: Mapped["Comment"] = relationship()
    manga: Mapped["Manga"] = relationship()

    @staticmethod
    def get_user_notifications(user, page=1):
        return Notification.query.filter_by(user_id=user.id).limit(Notification.page_size).offset((page-1) * Notification.page_size).all()

    @staticmethod
    def get_all_user_notification_count(user):
        return Notification.query.filter_by(user_id=user.id).count()

    @staticmethod
    def get_unread_user_notifications_count(user):
        return Notification.query.filter_by(user_id=user.id, is_read=False).count()

    def to_dict(self):
        return {
            "action": self.action,
            "id": self.id,
            "user": self.user.to_dict(),
            "type": self.type,
            "is_read": self.is_read,
            "created_at": self.created_at,
            "payload": self._render_payload()
        }

    def _render_payload(self):
        if self.type == "user":
            return {
                "actor": self.actor.to_dict(),
            }

        if self.type == "team":
            return {}

        if self.type == "comment":
            return {
                "actor": self.actor.to_dict(),
                "comment": self.comment.to_dict(),
            }

        if self.type == "manga":
            return {}

        if self.type == "chapter":
            pass