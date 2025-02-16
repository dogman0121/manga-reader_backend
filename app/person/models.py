from app import db
from sqlalchemy import Table, ForeignKey, and_
from datetime import datetime

subscriber = Table(
    'subscriber',
    db.metadata,
    db.Column('person_id', db.Integer, ForeignKey('person.id')),
    db.Column('user_id', db.Integer, ForeignKey('user.id')),
)

class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    creator_id = db.Column(db.Integer, ForeignKey("user.id"), nullable=False)
    creator = db.relationship("User", foreign_keys=creator_id)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get_by_name(name):
        return Person.query.filter_by(name=name).first()

    @staticmethod
    def get(person_id):
        return db.session.get(Person, person_id)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

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

