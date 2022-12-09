from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


chat_member_table = db.Table(
    'chat_members',
    db.Column('user_id', db.ForeignKey('users.id')),
    db.Column('chat_id', db.ForeignKey('chats.id')),
)


class _FormattedUrlModelMixin:
    _id_attribute: str = 'id'
    _name_attribute: str = 'name'
    _url_attribute: str = 'url_token'

    def __repr__(self) -> str:
        return "{class_name}{name_part}(id={id}, url={url})".format(
            class_name= self.__class__.__name__,
            name_part=' ' + self.__name if self.__name else '',
            id=self.__id,
            url=self.__url
        )

    @property
    def __id(self) -> str:
        return str(getattr(self, self._id_attribute))

    @property
    def __name(self) -> str:
        return str(getattr(self, self._name_attribute))

    @property
    def __url(self) -> str:
        return str(getattr(self, self._url_attribute))


class UserSession(db.Model):
    __tablename__ ='user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), nullable=False)
    cancellation_time = db.Column(db.DateTime, nullable=False)

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.cancellation_time


class User(db.Model, _FormattedUrlModelMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey(UserSession.id), unique=True, nullable=False)
    url_token = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(1024), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    avatar_path = db.Column(db.String(512))
    description = db.Column(db.String(256))

    session = db.relationship('UserSession', foreign_keys=(session_id, ))
    chats = db.relationship('Chat', secondary=chat_member_table, back_populates='members')


class Chat(db.Model, _FormattedUrlModelMixin):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    url_token = db.Column(db.String(32), nullable=False, unique=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String(256))

    members = db.relationship('User', secondary=chat_member_table, back_populates='chats')
    owner = db.relationship('User', foreign_keys=(owner_id, ))


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey(Chat.id), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    creation_time = db.Column(db.DateTime, default=datetime.now)
    message = db.Column(db.String(1024), nullable=False)
    pinned = db.Column(db.Boolean, nullable=False, default=False)

    author = db.relationship('User', foreign_keys=(author_id, ))
    chat = db.relationship('Chat', foreign_keys=(chat_id, ))

    def __repr__(self) -> str:
        return f"Message from user {self.author.url_token} in chat {self.chat.url_token}"
