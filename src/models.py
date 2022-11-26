from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


chat_member_table = db.Table(
    'chat_members',
    db.Column('user_id', db.ForeignKey('users.user_id')),
    db.Column('chat_id', db.ForeignKey('chats.chat_id')),
)


chat_member_role_table = db.Table(
    'chat_member_roles',
    db.Column('user_id', db.ForeignKey('users.user_id')),
    db.Column('chat_roles', db.ForeignKey('chat_roles.chat_role_id')),
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


class Token(db.Model):
    __tablename__ ='tokens'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256), nullable=False)
    cancellation_time = db.Column(db.DateTime, nullable=False)

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.cancellation_time


class User(db.Model, _FormattedUrlModelMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    refresh_token_id = db.Column(db.Integer, db.ForeignKey(Token.id), unique=True, nullable=False)
    access_token_id = db.Column(db.Integer, db.ForeignKey(Token.id), unique=True, nullable=False)
    url_token = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(1024), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    avatar_path = db.Column(db.String(512))
    description = db.Column(db.String(256))

    refresh_token = db.relationship('tokens', foreign_keys=(refresh_token_id, ))
    access_token = db.relationship('tokens', foreign_keys=(access_token_id, ))
    chats = db.relationship('Chat', secondary=chat_member_table, back_populates='members')
    roles = db.relationship('ChatRole', secondary=chat_member_role_table, back_populates='actors')





class Chat(db.Model, _FormattedUrlModelMixin):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    url_token = db.Column(db.String(32), nullable=False, unique=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String(256))

    members = db.relationship('User', secondary=chat_member_table, back_populates='chats')
    owner = db.relationship('User', foreign_keys=(owner_id, ))


class ChatRole(db.Model):
    __tablename__ = 'chat_roles'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey(Chat.id))
    name = db.Column(db.String(16), nullable=False)
    description = db.Column(db.String(256))
    hex_rgb_color = db.Column(db.String(6), nullable=False, default='FFFFFF')
    role_customization_rights = db.Column(db.Boolean, nullable=False, default=False)
    user_ban_rights = db.Column(db.Boolean, nullable=False, default=False)
    message_pinning_rights = db.Column(db.Boolean, nullable=False, default=False)
    styling_rights = db.Column(db.Boolean, nullable=False, default=False)

    chat = db.relationship('Chat', foreign_keys=(chat_id, ))
    actors = db.relationship('User', secondary=chat_member_role_table, back_populates='roles')

    def __repr__(self) -> str:
        return f"ChatRole {self.name} of {self.chat.url_token} chat with rights(customization={self.role_customization_rights}, ban={self.user_ban_rights}, message_pinning={self.message_pinning_rights}, styling={self.styling_rights})"


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
        return f"Message from user {self.author.user_url_token} in chat {self.chat.chat_url_token}"
