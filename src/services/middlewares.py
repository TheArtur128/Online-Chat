from abc import ABC, abstractmethod
from typing import Callable, Optional, Iterable
from functools import wraps

from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError

from services.factories import CustomArgumentFactory
from services.errors import StatusCodeError


class Middleware(ABC):
	def decorate(self, route: Callable) -> Callable:
		@wraps(route)
		def body(*args, **kwargs) -> any:
			return self.call_route(route, *args, **kwargs)

		return body

	@abstractmethod
	def call_route(self, route: Callable, *args, **kwargs) -> any:
		pass


class ProxyMiddleware(Middleware):
	def __init__(self, middlewares: Iterable[Middleware]):
		self.middlewares = list(middlewares)

	def call_route(self, route: Callable, *args, **kwargs) -> any:
		call_layer = route

		for middleware in self.middlewares:
			call_layer = CustomArgumentFactory(middleware.call_route, call_layer)

		call_layer(*args, **kwargs)


class ServiceErrorMiddleware(Middleware):
	def call_route(self, route: Callable, *args, **kwargs) -> any:
		try:
			return route(*args, **kwargs)
		except StatusCodeError as error:
			return (
				(
					error.messages
					if isinstance(error, ValidationError)
					else {'message': str(error)}
				),
				error.status_code
			)
		except ValidationError as error:
			return error.messages, 400


class DBMiddleware(Middleware, ABC):
	def __init__(self, database: SQLAlchemy):
		self.database = database


class DBSessionFinisherMiddleware(DBMiddleware):
	def call_route(self, route: Callable, *args, **kwargs) -> any:
		try:
			result = route(*args, **kwargs)
			self.database.session.commit()

			return result

		except Exception as error:
			self.database.session.rollback()

			raise error
