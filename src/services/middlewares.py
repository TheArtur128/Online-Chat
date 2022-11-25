from abc import ABC, abstractmethod
from typing import Callable, Optional
from functools import wraps

from marshmallow import ValidationError

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
