from abc import ABC, abstractmethod
from typing import Callable, Optional
from functools import wraps


class Middleware(ABC):
	def decorate(self, route: Callable) -> Callable:
		@wraps(route)
		def body(*args, **kwargs) -> any:
			return self.call_route(route, *args, **kwargs)

		return body

	@abstractmethod
	def call_route(self, route: Callable, *args, **kwargs) -> any:
		pass
