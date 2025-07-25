from app.domain.entities.user import User
from app.domain.repositories.user_repo import UserRepository
from app.infrastructure.models.user.sql_user import SQLUser


class SQLUserRepository(UserRepository):
    @staticmethod
    def _to_entity(user_model: SQLUser) -> User:
        return User(
            id=user_model.id,
            avatar=user_model.avatar,
            login=user_model.login,
            email=user_model.email,
            password=user_model.password,
            role=user_model.role,
        )

    def get_by_id(self, user_id: int) -> User:
        res = SQLUser.query.filter_by(id=user_id).first()
        return self._to_entity(res) if res else None

    def get_by_login(self, login: str) -> User:
        res = SQLUser.query.filter_by(login=login).first()
        return self._to_entity(res) if res else None

    def get_by_email(self, email: str) -> User:
        res = SQLUser.query.filter_by(email=email).first()
        return self._to_entity(res) if res else None