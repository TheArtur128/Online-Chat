from abc import ABC, abstractmethod


class IRouter(ABC):
    @abstractmethod
    def __call__(self, data: dict) -> any:
        pass
