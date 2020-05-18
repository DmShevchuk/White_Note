from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class EditNotesForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    body = TextAreaField('Запись', validators=[DataRequired()])
    is_important = BooleanField('Важная')
    image = FileField('Заменить изображение')
    current_image = StringField('Текущее изображение')
    place = StringField('Адрес')
    submit = SubmitField('Сохранить изменения')