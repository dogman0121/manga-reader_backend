from app import db
from app.models import Base

from sqlalchemy import Integer, Text, ForeignKey, DateTime, Column, Table, String, Select, func, asc, and_, Exists
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from datetime import datetime

class Vote(Base):
    __tablename__ = "vote"

    comment_id: Mapped[int] = mapped_column(Integer, ForeignKey("comment.id"), primary_key=True)
    comment: Mapped["Comment"] = relationship()
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)
    user: Mapped["User"] = relationship()
    type: Mapped[int] = mapped_column(Integer)

    def to_dict(self) -> dict:
        return {
            "comment": self.comment_id,
            "user": self.user_id,
            "type": self.type,
        }


    @staticmethod
    def get(manga_id, user_id):
        return db.session.execute(
            Select(Vote).where(and_(Vote.comment_id == manga_id, Vote.user_id == user_id))
        ).scalar()


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
    entity_type: Mapped[str] = mapped_column(nullable=True)
    entity_id: Mapped[int] = mapped_column(nullable=True)

    # manga: Mapped["Manga"] = relationship("Manga", secondary="manga_comment", back_populates="comments")
    # chapter: Mapped["Chapter"] = relationship("Chapter", secondary="chapter_comments", back_populates="comments")
    # post: Mapped["Post"] = relationship("Post", secondary="post_comment", back_populates="comments")

    @hybrid_property
    def manga(self):
        if self.entity_type != "manga":
            return None
        return db.session.query("Manga").filter_by(id=self.entity_id).first()

    @hybrid_property
    def chapter(self):
        if self.entity_type != "chapter":
            return None
        return db.session.query("Chapter").filter_by(id=self.entity_id).first()

    @hybrid_property
    def answers_count(self) -> int:
        return db.session.execute(
            Select(func.count(Comment.id))
            .where(Comment.parent_id == self.id)
        ).scalar()

    @hybrid_property
    def up_votes(self) -> int:
        return db.session.execute(
            Select(func.count("*")).where(and_(Vote.comment_id == self.id, Vote.type == 0))
        ).scalar()

    @hybrid_property
    def down_votes(self) -> int:
        return db.session.execute(
            Select(func.count("*")).where(and_(Vote.comment_id == self.id, Vote.type == 1))
        ).scalar()

    def is_voted_by_user(self, user) -> bool:
        if user is None:
            return False

        return self.get_user_vote(user) is not None

    def get_user_vote(self, user):
        if user is None:
            return None

        return db.session.execute(
            Select(Vote)
            .where(and_(Vote.user_id == user.id, Vote.comment_id == self.id))
        ).scalar()

    @staticmethod
    def get_manga_comments(manga_id, page=1):
        return db.session.execute(
            Select(Comment)
            .filter_by(entity_type="manga", entity_id=manga_id)
            .order_by(asc(Comment.created_at))
            .limit(Comment.page_size)
            .offset((page - 1) * Comment.page_size)
        ).scalars().all()

    @staticmethod
    def get_chapter_comments(chapter_id, page=1):
        return db.session.execute(
            Select(Comment)
            .filter_by(entity_type="chapter", entity_id=chapter_id)
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

    def add_vote(self, user_id, vote_type):
        vote = Vote(comment_id=self.id, user_id=user_id, type=vote_type)

        vote.add()

    def delete_vote(self, user_id):
        vote = Vote.get(self.id, user_id)

        if vote is not None:
            vote.delete()

    def to_dict(self, user=None) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "user": self.creator.to_dict(),
            "answers_count": self.answers_count,
            "created_at": datetime.strftime(self.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "up_votes": self.up_votes,
            "down_votes": self.down_votes,
            "user_vote": self.get_user_vote(user).type if self.get_user_vote(user) else None,
        }



class MangaComment(Base):
    __tablename__ = 'manga_comment'

    manga_id: Mapped[int] = mapped_column(ForeignKey('manga.id'), nullable=False, primary_key=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey('comment.id'), nullable=False, primary_key=True)

class ChapterComment(Base):
    __tablename__ = 'chapter_comment'

    chapter_id: Mapped[int] = mapped_column(ForeignKey('chapter.id'), nullable=False, primary_key=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey('comment.id'), nullable=False, primary_key=True)


# class PostComment(Base):
#     __tablename__ = 'post_comment'
#
#     post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable=False, primary_key=True)
#     comment_id: Mapped[int] = mapped_column(ForeignKey('comment.id'), nullable=False, primary_key=True)