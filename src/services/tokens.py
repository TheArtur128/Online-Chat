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


class TokenPromiser(ITokenPromiser):
    def __init__(self, token_decoder: ITokenDecoder):
        self.token_decoder = token_decoder

    def __call__(self, token: Optional[str]) -> None:
        if not token:
            raise MissingTokenError("Token is missing")
        
        if self.token_decoder.decode(token) is TokenDecoderResult.INCORRECT:
            raise InvalidTokenError("Token is invalid")