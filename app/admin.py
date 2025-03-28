from app import db
from app.user.models import User
from app.manga.models import Manga, Genre, Status, NameTranslation, Type, Adult
from app.person.models import Person
from app.comment.models import Comment
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


admin = Admin(url="/api/admin")


class UserAdmin(ModelView):
    column_list = ('id', 'login', 'email', 'role', 'created_at')

    form_columns = ['login', 'email', 'role', 'created_at']


class TitleAdmin(ModelView):
    column_list = ('id', 'name', 'type_id', 'status_id', 'year', 'views', 'description', 'year', 'views', 'adult'
                   'creator_id', 'created_at')
    form_columns = ['name', 'type_id', 'status_id', 'year', 'description', 'year', 'views', 'adult']


class NameTranslationAdmin(ModelView):
    column_list = ('manga_id', 'lang', 'name')

class PersonAdmin(ModelView):
    column_list = ('id', 'name', 'creator_id', 'created_at')

    form_columns = ['id', 'name', 'creator_id', 'created_at']

class CommentAdmin(ModelView):
    column_list = ('id', 'text', 'user_id', 'created_at')

admin.add_view(UserAdmin(User, db.session, endpoint="users"))
admin.add_view(TitleAdmin(Manga, db.session, endpoint="titles"))
admin.add_view(ModelView(Genre, db.session, endpoint="genres"))
admin.add_view(ModelView(Status, db.session, endpoint="statuses"))
admin.add_view(ModelView(Type, db.session, endpoint="types"))
admin.add_view(ModelView(Adult, db.session, endpoint="adults"))
admin.add_view(PersonAdmin(Person, db.session, endpoint="persons"))
admin.add_view(CommentAdmin(Comment, db.session, endpoint="comments"))
admin.add_view(NameTranslationAdmin(NameTranslation, db.session, endpoint="name-translations"))