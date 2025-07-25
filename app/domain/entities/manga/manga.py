from dataclasses import dataclass

@dataclass
class Manga:
    id: int
    slug: str
    name: str
    views: int
    verified: bool
