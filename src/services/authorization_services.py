from abc import ABC, abstractmethod


class IUserRegistrar(ABC):
	@abstractmethod
	def __call__(self, user_data: dict) -> None:
		pass
