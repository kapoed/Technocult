from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed

class QuestionForm(FlaskForm):
    title = StringField(
        'Тема вашего вопроса',
        validators=[
            DataRequired(message="Пожалуйста, введите тему вопроса."),
            Length(min=5, max=200, message="Тема должна содержать от 5 до 200 символов.")
        ],
    )
    content = TextAreaField(
        'Подробно опишите ваш вопрос (необязательно)',
        validators=[Length(max=5000)],
    )
    image = FileField(
        'Прикрепить изображение (необязательно)',
        validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Разрешены только изображения (jpg, png, jpeg, gif)!')]
    )
    submit = SubmitField('Опубликовать вопрос')
