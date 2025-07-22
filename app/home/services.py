from ..manga.repositories import MangaRepository

class HomeService:
    def __init__(self):
        pass

    @staticmethod
    def get_newest_manga():
        manga = MangaRepository.get_newest()
        return manga

    @staticmethod
    def get_ended_manga(self):
        pass

    @staticmethod
    def get_featured_manga(self):
        pass

    @staticmethod
    def get_user_history(self, user):
        pass