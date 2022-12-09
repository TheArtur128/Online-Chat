from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Iterable

from models import Token, User
from services.abstractions.interfaces import IJWTCoder
from services.utils import get_time_after
from services.jwt_serializers import JWTSerializator




class TokenFactory(ABC):
    _original_token_factory: Callable[[str, datetime], Token] = Token

    def __call__(self) -> Token:
        return self._original_token_factory(
            body=self._create_token_body(),
            cancellation_time=self._get_token_cancellation_time()
        )

    @abstractmethod
    def _create_token_body(self) -> str:
        pass

    @abstractmethod
    def _get_token_cancellation_time(self) -> datetime:
        pass


class MinuteTokenFactory(TokenFactory, ABC):
    _token_life_minutes: int | float

    def _get_token_cancellation_time(self) -> datetime:
        return datetime.fromtimestamp(
            datetime.now().timestamp() + self._token_life_minutes*60
        )


class CustomMinuteTokenFactory(MinuteTokenFactory):
    def __init__(self, token_life_minutes: int | float, token_body_factory: Callable[[], str]):
        self.token_life_minutes = token_life_minutes
        self.token_body_factory = token_body_factory

    @property
    def token_life_minutes(self) -> int | float:
        return self._token_life_minutes

    @token_life_minutes.setter
    def token_life_minutes(self, minutes: int | float) -> None:
        self._token_life_minutes = minutes

    def _create_token_body(self) -> str:
        return self.token_body_factory()


class UserAccessTokenFactory:
    def __init__(self, jwt_coder: IJWTCoder, life_minutes: int | float):
        self.jwt_coder = jwt_coder
        self.life_minutes = life_minutes

    def __call__(self, user: User) -> str:
        return self.jwt_coder.encode({
            'url_token': user.url_token,
            'exp': get_time_after(self.life_minutes, is_time_raw=True)
        })
