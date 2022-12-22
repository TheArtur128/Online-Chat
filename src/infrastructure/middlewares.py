from typing import Callable, Optional

from flask_middlewares import Middleware
from jwt import InvalidTokenError

from infrastructure.controllers import ControllerResponse
from infrastructure.errors import AccessTokenInvalidError
from services.errors import MissingTokenError, InvalidTokenError
from services.tokens import TokenPromiser


class AccessTokenRequiredMiddleware(Middleware):
    def __init__(
        self,
        access_token_promiser: TokenPromiser,
        access_token_getter: Callable[[], Optional[str]]
    ):
        self.access_token_promiser = access_token_promiser
        self.access_token_getter = access_token_getter

    def call_route(self, route: Callable, *args, **kwargs) -> any:
        access_token = self.access_token_getter()

        try:
            self.access_token_promiser(access_token)
        except MissingTokenError:
            raise AccessTokenInvalidError("Access token is missing")
        except InvalidTokenError:
            raise AccessTokenInvalidError("Access token is invalid")

        return route(*args, **kwargs)


class ControllerResponseFormatterMiddleware(Middleware):
    def __init__(self, response_formatter: Callable[[ControllerResponse], any]):
        self.response_formatter = response_formatter

    def call_route(self, route: Callable, *args, **kwargs) -> any:
        result = route(*args, **kwargs)

        return (
            self.response_formatter(result)
            if isinstance(result, ControllerResponse)
            else result
        )