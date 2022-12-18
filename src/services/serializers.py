from abc import ABC, abstractmethod


class ICoder(ABC):
    @abstractmethod
    def encode(self, data: dict) -> str:
        pass


class IDecoder(ABC):
    @abstractmethod
    def decode(self, token: str) -> dict:
        pass


class ISerializator(ICoder, IDecoder, ABC):
    pass