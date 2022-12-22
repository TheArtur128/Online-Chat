from abc import ABC, abstractmethod
from typing import Optional


class ITokenCoder(ABC):
    @abstractmethod
    def encode(self, data: dict) -> str:
        pass


class ITokenDecoder(ABC):
    @abstractmethod
    def decode(self, token: str) -> dict | TokenDecoderResult:
        pass


class ITokenSerializator(ITokenCoder, ITokenDecoder, ABC):
    pass


