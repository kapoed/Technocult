from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from data.db_session import create_session
from data.users import User


class RegistrationForm(FlaskForm):
    login = StringField('Придумайте логин', validators=[DataRequired(message="Поле обязательно")])
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

    def validate_login(self, login):
        session = create_session()
        user = session.query(User).filter(User.login == login.data).first()
        if user is not None:
            raise ValidationError('Логин занят')

    def validate_email(self, email):
        session = create_session()
        user = session.query(User).filter(User.email == email.data).first()
        if user is not None:
            raise ValidationError('Пользователь с таким Email уже зарегистрирован')