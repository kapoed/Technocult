from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Length

VALID_ENTRY_TYPES_CHOICES = [
    ('articles', 'Статья'),
    ('instructions', 'Инструкция'),
    ('guides', 'Гайд')
]


class KnowledgeEntryForm(FlaskForm):
    title = StringField(
        'Название записи',
        validators=[
            DataRequired(message="Пожалуйста, введите название."),
            Length(min=5, max=250, message="Название должно содержать от 5 до 250 символов.")
        ],
        render_kw={"placeholder": "Введите полное название статьи, инструкции или гайда"}
    )

    entry_type = SelectField(
        'Тип записи',
        choices=VALID_ENTRY_TYPES_CHOICES,
        validators=[DataRequired(message="Пожалуйста, выберите тип записи.")]
    )

    main_image = FileField(
        'Основное изображение (обязательно)',
        validators=[
            FileRequired(message="Пожалуйста, загрузите основное изображение."),
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Разрешены только изображения (jpg, jpeg, png, gif)!')
        ]
    )

    content = TextAreaField(
        'Полное содержание записи (поддерживает Markdown)',
        validators=[DataRequired(message="Пожалуйста, введите содержание записи.")],
        render_kw={"rows": 20,
                   "placeholder": "Введите текст вашей записи здесь. Вы можете использовать Markdown для форматирования..."}
    )

    submit = SubmitField('Опубликовать запись')
