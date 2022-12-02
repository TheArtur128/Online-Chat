from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Iterable
from secrets import token_hex

from config import SECRET_KEY, ACCESS_TOKEN_LIFE_MINUTES, REFRESH_TOKEN_LIFE_DAYS
from models import Token, User
from services.abstractions.interfaces import IJWTCoder
from services.utils import get_time_after
from services.jwt_serializers import JWTSerializator


class ArgumentFactory(ABC):
    _original_factory: Callable
    _args: tuple
    _kwargs: dict

    _is_input_arguments_first: bool = False

    def __call__(self, *args, **kwargs) -> any:
        args = [args, self._args]

        if self._is_input_arguments_first:
            args.reverse()

        return self._original_factory(
            *(args[0] + args[1]),
            **self._kwargs,
            **kwargs
        )


class CustomArgumentFactory(ArgumentFactory):
    def __init__(self, original_factory: Callable, *args, is_input_arguments_first: bool = True, **kwargs):
        self._original_factory = original_factory
        self.args = args
        self.kwargs = kwargs
        self._is_input_arguments_first = is_input_arguments_first

    @property
    def args(self) -> tuple:
        return self._args

    @args.setter
    def args(self, args: Iterable) -> None:
        self._args = tuple(args)

    @property
    def kwargs(self) -> dict:
        return self._kwargs

    @kwargs.setter
    def kwargs(self, kwargs: dict) -> None:
        self._kwargs = dict(kwargs)

    @property
    def is_input_arguments_first(self) -> bool:
        return self._is_input_arguments_first

    @is_input_arguments_first.setter
    def is_input_arguments_first(self, is_input_arguments_first: bool) -> None:
        self._is_input_arguments_first = is_input_arguments_first


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


DEFAULT_JWT_SERIALIZATOR_FACTORY = CustomArgumentFactory(JWTSerializator, SECRET_KEY)

DEFAULT_ACCESS_TOKEN_FACTORY = UserAccessTokenFactory(
    DEFAULT_JWT_SERIALIZATOR_FACTORY(),
    ACCESS_TOKEN_LIFE_MINUTES
)

DEFAULT_REFRESH_TOKEN_FACTORY = CustomMinuteTokenFactory(
    REFRESH_TOKEN_LIFE_DAYS*24*60,
    CustomArgumentFactory(token_hex, Token.body.comparator.type.length // 2)
)
