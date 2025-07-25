
class SQLBaseModel:

    def update(self, db, data, commit=True):

        for key, value in data.items():
            setattr(self, key, value)

        if commit:
            db.commit()

    def save(self, db, commit=True):
        db.session.add(self)

        if commit:
            db.session.commit()

    def delete(self, db, commit=True):
        db.session.delete(self)

        if commit:
            db.session.commit()

