from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum, auto

from services.errors import MissingTokenError, InvalidTokenError


class ITokenCoder(ABC):
    @abstractmethod
    def encode(self, data: dict) -> str:
        pass


class TokenDecoderResult(Enum):
    INCORRECT = auto()


class ITokenDecoder(ABC):
    @abstractmethod
    def decode(self, token: str) -> dict | TokenDecoderResult:
        pass


class ITokenSerializator(ITokenCoder, ITokenDecoder, ABC):
    pass


class ITokenPromiser(ABC):
    @abstractmethod
    def __call__(self, token: Optional[str]) -> None:
        pass


