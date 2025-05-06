from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(message="Поле обязательно")])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Поле обязательно"),
        Length(min=6, message="Минимум 6 символов")
    ])
    submit = SubmitField('Отправить')
