from abc import ABC, abstractmethod
from typing import Callable

from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash

from services.middlewares import DBMiddleware, DBSessionFinisherMiddleware
from services.errors import UserAlreadyExistsError
from schemes import Schema, FullUserSchema
from models import User


class IUserRegistrar(ABC):
	@abstractmethod
	def __call__(self, user_data: dict) -> None:
		pass


class DBUserRegistrar(IUserRegistrar):
	def __init__(self, database: SQLAlchemy):
		self.__db_connection_middleware = self.__db_connection_middleware_factory(database)

	@property
	def database(self) -> SQLAlchemy:
		return self.__db_connection_middleware.database

	@database.setter
	def database(self, database: SQLAlchemy) -> None:
		self.__db_connection_middleware.database = database

	def __call__(self, user_data: dict) -> None:
		self.__db_connection_middleware.call_route(self._register_user, user_data)

	def _register_user(self, user_data: dict) -> None:
		user_data = self._prepare_user_data(user_data)

		if User.query.filter_by(user_url_token=user_data['user_url_token']).first():
			raise UserAlreadyExistsError(
				f"User with \"{user_data['user_url_token']}\" url token already exists"
			)

		self.database.session.add(User(**user_data))

	def _prepare_user_data(self, user_data: dict) -> dict:
		errors = self.__user_data_schema.validate(user_data)

		if not 'password' in user_data.keys():
			errors['password'] = ['Password is required.']

		if errors:
			raise ValidationError(errors)

		user_data['password_hash'] = generate_password_hash(user_data['password'])
		del user_data['password']

		return self.__user_data_schema.dump(user_data)

	__user_data_schema: Schema = FullUserSchema()
	__db_connection_middleware_factory: Callable[[SQLAlchemy], DBMiddleware] = DBSessionFinisherMiddleware
