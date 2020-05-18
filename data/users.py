import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


# Модель пользователя
class Users(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)

    notes = sqlalchemy.orm.relation('Notes', back_populates='user')

    def generate_hashed_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_hashed_password(self, password):
        return check_password_hash(self.hashed_password, password)
