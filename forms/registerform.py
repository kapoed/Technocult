from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError


class RegistrationForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(message="Поле обязательно")])
    last_name = StringField('Фамилия', validators=[DataRequired(message="Поле обязательно")])
    email = StringField('Email', validators=[
        DataRequired(message="Поле обязательно"),
        Email(message="Неверный формат email")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Поле обязательно"),
        Length(min=6, message="Минимум 6 символов")
    ])
    # remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Отправить')
