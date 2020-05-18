from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Класс формы поиска
class SearchForm(FlaskForm):
    search = StringField('Поиск по записям', validators=[DataRequired()])
    submit = SubmitField('Поиск')
