from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(1024), nullable=False)
    avatar_path = db.Column(db.String(512))
    description = db.Column(db.String(256))
    status = db.Column(db.String(1))


class Chat(db.Model):
    __tablename__ = 'chats'

    chat_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.user_id), nullable=False)
    name = db.Column(db.String(64))
    description = db.Column(db.String(256))

    owner = db.relationship("User", foreign_keys=(owner_id, ))


class ChatRole(db.Model):
    __tablename__ = 'chat_roles'

    chat_role_id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey(Chat.chat_id))
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    hex_rgb_color = db.Column(db.String(6), nullable=False, default='FFFFFF')
    role_customization_rights = db.Column(db.Boolean, nullable=False, default=False)
    user_ban_rights = db.Column(db.Boolean, nullable=False, default=False)
    message_pinning_rights = db.Column(db.Boolean, nullable=False, default=False)
    styling_rights = db.Column(db.Boolean, nullable=False, default=False)

    chat = db.relationship("Chat", foreign_keys=(chat_id, ))


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    chat_message_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.user_id), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey(Chat.chat_id), nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.now)
    message = db.Column(db.String(1024), nullable=False)
    pinned = db.Column(db.Boolean, nullable=False, default=False)

    author = db.relationship("User", foreign_keys=(author_id, ))
    chat = db.relationship("Chat", foreign_keys=(chat_id, ))
