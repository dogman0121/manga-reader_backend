from .models import Manga

class MangaRepository:
    def __init__(self):
        pass

    @staticmethod
    def get_all():
        pass

    @staticmethod
    def get_by_id(manga_id):
        return Manga.query.filter_by(id=manga_id).scalar()

    @staticmethod
    def get_newest():
        return (
            Manga.query.order_by(Manga.created_at.desc()).limit(10).all()
        )

    @staticmethod
    def get_ended():
        return (
            Manga.query.order_by(Manga.type_id).limit(10).all()
        )
