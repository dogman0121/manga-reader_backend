from app import db

class Base(db.Model):
    __abstract__ = True

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.verified = True
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()