from abc import ABC, abstractmethod
from typing import Iterable


class IRouter(ABC):
    @abstractmethod
    def __call__(self, data: dict | Iterable) -> any:
        pass


class IJWTCoder(ABC):
    @abstractmethod
    def encode(self, data: dict) -> str:
        pass


class IJWTDecoder(ABC):
    @abstractmethod
    def decode(self, token: str) -> dict:
        pass
