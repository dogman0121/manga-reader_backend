from app import db
from app.models import Base
from sqlalchemy import Table, ForeignKey, and_, Column, Integer, String, DateTime, Select, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from app.user.models import User

subscriber = Table(
    'subscriber',
    db.metadata,
    Column('person_id', Integer, ForeignKey('person.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
)

class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    creator: Mapped["User"] = relationship("User")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @staticmethod
    def get_by_name(name):
        return Person.query.filter_by(name=name).first()

    @staticmethod
    def get(person_id):
        return db.session.get(Person, person_id)

    @staticmethod
    def search(query):
        return db.session.execute(
            Select(Person).filter(func.lower(Person.name).like(f"%{query.lower()}%"))
        ).scalars().all()

    def add_subscriber(self, user_id):
        db.session.execute(subscriber.insert().values(person_id=self.id, user_id=user_id))
        db.session.commit()

    def remove_subscriber(self, user_id):
        db.session.execute(subscriber.delete().where(and_(subscriber.c.person_id == self.id,
                                                          subscriber.c.user_id == user_id)))
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'creator': self.creator.to_dict(),
            'created_at': datetime.strftime(self.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        }

