from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
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


    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_url_token = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(1024), nullable=False)
    public_username = db.Column(db.String(32))
    avatar_path = db.Column(db.String(512))
    description = db.Column(db.String(256))

    chats = db.relationship('Chat', secondary=chat_member_table, back_populates='members')
    roles = db.relationship('ChatRole', secondary=chat_member_role_table, back_populates='actors')

    @property
    def name(self) -> str:
        return self.public_username if self.public_username else self.user_url_token

class Chat(db.Model):
    __tablename__ = 'chats'

    chat_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.user_id), nullable=False)
    chat_url_token = db.Column(db.String(32), nullable=False, unique=True)
    public_chat_name = db.Column(db.String(32))
    description = db.Column(db.String(256))

    members = db.relationship('User', secondary=chat_member_table, back_populates='chats')
    owner = db.relationship('User', foreign_keys=(owner_id, ))

    @property
    def name(self) -> str:
        return self.public_chat_name if self.public_chat_name else self.chat_url_token


class ChatRole(db.Model):
    __tablename__ = 'chat_roles'

    chat_role_id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey(Chat.chat_id))
    chat_role_name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    hex_rgb_color = db.Column(db.String(6), nullable=False, default='FFFFFF')
    role_customization_rights = db.Column(db.Boolean, nullable=False, default=False)
    user_ban_rights = db.Column(db.Boolean, nullable=False, default=False)
    message_pinning_rights = db.Column(db.Boolean, nullable=False, default=False)
    styling_rights = db.Column(db.Boolean, nullable=False, default=False)

    chat = db.relationship('Chat', foreign_keys=(chat_id, ))
    actors = db.relationship('User', secondary=chat_member_role_table, back_populates='roles')


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    chat_message_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.user_id), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey(Chat.chat_id), nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.now)
    message = db.Column(db.String(1024), nullable=False)
    pinned = db.Column(db.Boolean, nullable=False, default=False)

    author = db.relationship('User', foreign_keys=(author_id, ))
    chat = db.relationship('Chat', foreign_keys=(chat_id, ))
