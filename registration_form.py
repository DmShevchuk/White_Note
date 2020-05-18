from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField


# Класс формы регистрации
class RegistrationForm(FlaskForm):
    login = StringField('Ваш логин', validators=[DataRequired()])
    email = EmailField('Ваша почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль ещё раз', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
