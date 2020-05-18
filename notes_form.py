from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


# Класс формы добавления записей
class NotesForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    body = TextAreaField('Запись', validators=[DataRequired()])
    is_important = BooleanField('Важная')
    image = FileField('Добавить изображение')
    place = StringField('Адрес')
    submit = SubmitField('Сохранить')
