from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed

class AnswerForm(FlaskForm):
    content = TextAreaField(
        'Ваш ответ',
        validators=[
            DataRequired(message="Пожалуйста, введите текст ответа."),
            Length(min=1, max=5000, message="Ответ должен содержать от 1 до 5000 символов.")
        ],
        render_kw={"placeholder": "Поделитесь своим решением или мнением...", "rows": 5}
    )
    image = FileField(
        'Прикрепить изображение (необязательно)',
        validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Разрешены только изображения (jpg, png, jpeg, gif)!')]
    )
    submit = SubmitField('Отправить ответ')
