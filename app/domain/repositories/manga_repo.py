from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.manga.manga import Manga


class MangaRepository(ABC):
    @abstractmethod
    def get_newest(self, verified: bool = None) -> List[Manga]:
        pass

    @abstractmethod
    def get_most_viewed(self, verified: bool = None) -> List[Manga]:
        pass

    @abstractmethod
    def get_ended(self, verified: bool = None) -> List[Manga]:
        pass