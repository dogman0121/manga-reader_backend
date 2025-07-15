from .models import ListManga, List

class ListService:
    def __init__(self):
        pass

    @staticmethod
    def get_list(list_id):
        return List.query.get(list_id)

    @staticmethod
    def get_user_lists_with_manga(manga, user):
        return List.query.join(ListManga, ListManga.list_id == List.id).filter(
            ListManga.manga_id == manga.id,
            List.creator_id == user.id
        ).all()