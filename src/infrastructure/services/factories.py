from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Iterable

from infrastructure.repositories import IRepository
from infrastructure.errors import UserAlreadyExistsError
from orm.models import UserSession, User
from tools.jwt_serializers import IJWTCoder
from tools.utils import get_time_after



class UserSessionFactory(ABC):
    _original_user_session_factory: Callable[[str, datetime], UserSession] = UserSession

    def __call__(self) -> UserSession:
        return self._original_token_factory(
            token=self._create_user_session_token(),
            cancellation_time=self._get_session_cancellation_time()
        )

    @abstractmethod
    def _create_user_session_token(self) -> str:
        pass

    @abstractmethod
    def _get_session_cancellation_time(self) -> datetime:
        pass


class MinuteUserSessionFactory(UserSessionFactory, ABC):
    _user_session_life_minutes: int | float

    def _get_session_cancellation_time(self) -> datetime:
        return datetime.fromtimestamp(
            datetime.now().timestamp() + self._user_session_life_minutes*60
        )


class CustomMinuteUserSessionFactory(MinuteUserSessionFactory):
    def __init__(self, user_session_life_minutes: int | float, user_session_token_factory: Callable[[], str]):
        self.user_session_life_minutes = user_session_life_minutes
        self.user_session_token_factory = user_session_token_factory

    @property
    def user_session_life_minutes(self) -> int | float:
        return self._user_session_life_minutes

    @user_session_life_minutes.setter
    def user_session_life_minutes(self, minutes: int | float) -> None:
        self._user_session_life_minutes = minutes

    def _create_user_session_token(self) -> str:
        return self.user_session_token_factory()


class UserAccessTokenFactory:
    def __init__(self, jwt_coder: IJWTCoder, life_minutes: int | float):
        self.jwt_coder = jwt_coder
        self.life_minutes = life_minutes

    def __call__(self, user: User) -> str:
        return self.jwt_coder.encode({
            'url_token': user.url_token,
            'exp': get_time_after(self.life_minutes, is_time_raw=True)
        })
