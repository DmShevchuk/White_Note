from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired


# Класс формы переводчика
class TranslateForm(FlaskForm):
    first_language = SelectField('С', choices=[('ru', 'Русского'), ('en', 'Английского'), ('es', 'Испанского'),
                                               ('zh', 'Китайского'),
                                               ('de', 'Немецкого'), ('fr', 'Французского')])

    text_for_translate = TextAreaField('Введите текст здесь', validators=[DataRequired()])

    second_language = SelectField('На', choices=[('en', 'Английский'), ('es', 'Испанский'), ('zh', 'Китайский'),
                                                 ('de', 'Немецкий'), ('ru', 'Русский'), ('fr', 'Французский')])

    translated_text = TextAreaField('Перевод появится здесь')
    submit = SubmitField('Перевод')
