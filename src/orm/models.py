from datetime import datetime

from orm import db


class UserSession(db.Model):
    __tablename__ ='user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), nullable=False)
    cancellation_time = db.Column(db.DateTime, nullable=False)

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.cancellation_time


class User(_FormattedUrlModelMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey(UserSession.id), unique=True)
    url_token = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(1024), nullable=False)

    session = db.relationship('UserSession', foreign_keys=(session_id, ))
