from app import db

from .models import Chapter

class ChapterService:
    def __init__(self):
        pass

    @staticmethod
    def get_chapter(chapter_id=None):
        if chapter_id:
            return Chapter.query.get(chapter_id)

    @staticmethod
    def create_chapter(chapter: Chapter):
        db.session.add(chapter)
        db.session.commit()