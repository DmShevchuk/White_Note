from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField


# Класс формы редактирования профиля
class ProfileForm(FlaskForm):
    login = StringField('Ваш логин', validators=[DataRequired()])
    email = EmailField('Ваша почта', validators=[DataRequired()])
    old_password = PasswordField('Старый пароль')
    new_password = PasswordField('Новый пароль')
    new_password_again = PasswordField('Новый пароль ещё раз')
    submit = SubmitField('Сохранить изменения')
