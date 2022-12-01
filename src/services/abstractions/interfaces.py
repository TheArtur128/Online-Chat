from abc import ABC, abstractmethod
from typing import Iterable


class IRouter(ABC):
    @abstractmethod
    def __call__(self, data: dict | Iterable) -> any:
        pass