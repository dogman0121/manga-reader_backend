from app.domain.exceptions import PermissionException
from app.domain.permissions.manga_permission import MangaPermission
from app.domain.services.manga_service import MangaService


class GetManga:
    def __init__(self, manga_repo):
        self.manga_repo = manga_repo

    def execute(self, manga_slug, user=None):
        manga = MangaService(self.manga_repo).get_manga(slug=manga_slug)

        if not MangaPermission(manga, user).can_view():
            raise PermissionException

        return manga