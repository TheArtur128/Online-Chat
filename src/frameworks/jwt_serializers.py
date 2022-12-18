from services.serializers import ISerializator

from jwt import encode, decode
from datetime import datetime


class JWTSerializator(ISerializator):
    def __init__(self, key: str, is_symmetric: bool = True, leeway: int | float = 0):
        self.key = key
        self.is_symmetric = is_symmetric
        self.leeway = leeway

    @property
    def algorithm(self) -> str:
        return 'HS256' if self.is_symmetric else 'RS256'

    def encode(self, data: dict, *, headers: dict = dict()) -> str:
        return encode(data, key=self.key, algorithm=self.algorithm, headers=headers)

    def decode(self, token: str) -> dict:
        return decode(token, key=self.key, algorithms=(self.algorithm, ), leeway=self.leeway)
