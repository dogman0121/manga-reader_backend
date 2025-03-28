from app import db
from app.models import Base

from sqlalchemy import Integer, Text, ForeignKey, DateTime, Column, Table, String, Select, func, asc
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from datetime import datetime

class Comment(Base):
    page_size = 8

    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    root_id: Mapped[int] = mapped_column(ForeignKey("comment.id"), nullable=True)
    root: Mapped["Comment"] = relationship(primaryjoin="Comment.root_id == Comment.id")
    parent_id: Mapped[int] = mapped_column(ForeignKey("comment.id"), nullable=True)
    parent: Mapped["Comment"] = relationship(primaryjoin="Comment.parent_id == Comment.id")
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    creator: Mapped["User"] = relationship('User', backref='comments')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda x: datetime.utcnow(), nullable=False)
    manga: Mapped["Manga"] = relationship("Manga", secondary="manga_comment", back_populates="comments")

    @hybrid_property
    def answers_count(self) -> int:
        return db.session.execute(
            Select(func.count(Comment.id))
            .where(Comment.parent_id == self.id)
        ).scalar()

    @staticmethod
    def get(comment_id: int) -> "Comment":
        return db.session.get(Comment, comment_id)

    @staticmethod
    def get_manga_comments(manga_id, page=1):
        return db.session.execute(
            Select(Comment)
            .join(MangaComment)
            .filter_by(manga_id=manga_id)
            .order_by(asc(Comment.created_at))
            .limit(Comment.page_size)
            .offset((page - 1) * Comment.page_size)
        ).scalars().all()

    @staticmethod
    def get_comment_children(comment_id, page=1):
        return db.session.execute(
            Select(Comment)
            .filter_by(parent_id=comment_id)
            .order_by(asc(Comment.created_at))
            .limit(Comment.page_size)
            .offset((page - 1) * Comment.page_size)
        ).scalars().all()

    @staticmethod
    def get_comment_descendants(comment_id, page=1):
        return db.session.execute(
            Select(Comment)
            .filter_by(root_id=comment_id)
            .order_by(asc(Comment.created_at))
            .limit(Comment.page_size)
            .offset((page - 1) * Comment.page_size)
        ).scalars().all()


    def add_for_manga(self, manga_id):
        self.add()
        MangaComment(manga_id=manga_id, comment_id=self.id).add()

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "user": self.creator.to_dict(),
            "answers_count": self.answers_count,
            "created_at": datetime.strftime(self.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        }



class MangaComment(Base):
    __tablename__ = 'manga_comment'

    manga_id: Mapped[int] = mapped_column(ForeignKey('manga.id'), nullable=False, primary_key=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey('comment.id'), nullable=False, primary_key=True)
