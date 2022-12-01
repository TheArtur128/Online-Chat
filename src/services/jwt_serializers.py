from abc import ABC, abstractmethod

from jwt import encode, decode
from datetime import datetime

from services.abstractions.interfaces import IJWTSerializator


class JWTSerializator:
    def __init__(self, key: str, is_symmetric: bool = True):
        self.key = key
        self.is_symmetric = is_symmetric

    @property
    def algorithm(self) -> str:
        return 'HS256' if self.is_symmetric else 'RS256'

    def encode(self, data: dict) -> str:
        return encode(data, key=self.key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        return decode(token, key=self.key, algorithms=self.algorithm)