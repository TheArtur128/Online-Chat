from abc import ABC, abstractmethod

from jwt import encode, decode
from datetime import datetime

from services.abstractions.interfaces import IJWTSerializator


class JWTSerializator(IJWTSerializator):
    def __init__(self, key: str, is_symmetric: bool = True, leeway: int | float = 0):
        self.key = key
        self.is_symmetric = is_symmetric
        self.leeway = leeway

    @property
    def algorithm(self) -> str:
        return 'HS256' if self.is_symmetric else 'RS256'

    def encode(self, data: dict) -> str:
        return encode(data, key=self.key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        return decode(token, key=self.key, algorithms=(self.algorithm, ), leeway=self.leeway)
