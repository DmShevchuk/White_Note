import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Модель записи
class Notes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'notes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    body = sqlalchemy.Column(sqlalchemy.String)
    images = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_important = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = sqlalchemy.orm.relation('Users')