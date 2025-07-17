from sqlalchemy.orm import Mapped, mapped_column

from app import db

from datetime import datetime

class Base(db.Model):
    __abstract__ = True

    @classmethod
    def get(cls, entity_id):
        return db.session.get(cls, entity_id)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class File:
    __abstract__ = True

    uuid: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    orig_filename: Mapped[str] = mapped_column(nullable=True)
    ext: Mapped[str] = mapped_column(nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda x: datetime.now())