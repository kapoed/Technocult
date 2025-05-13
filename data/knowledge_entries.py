import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class KnowledgeEntry(SqlAlchemyBase):
    __tablename__ = 'knowledge_entries'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    entry_type = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)

    main_image_filename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)  # Будет храниться Markdown

    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now, index=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    def __repr__(self):
        return f"<KnowledgeEntry {self.id} '{self.title}' ({self.entry_type}) by User {self.user_id}>"
