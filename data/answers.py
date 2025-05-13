# data/answers.py
import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Answer(SqlAlchemyBase):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    image_filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    question_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("questions.id"))
    question = orm.relationship('Question', back_populates='answers')

    def __repr__(self):
        return f"<Answer {self.id} to Question {self.question_id} by User {self.user_id}>"
