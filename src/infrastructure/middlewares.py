from typing import Callable, Optional

from flask_middlewares import Middleware
from jwt import InvalidTokenError

from infrastructure.controllers import ControllerResponse
from infrastructure.errors import AccessTokenInvalidError
from services.serializers import IDecoder


class AccessTokenRequiredMiddleware(Middleware):
    def __init__(self, token_decoder: IDecoder, access_token_getter: Callable[[], Optional[str]]):
        self.token_decoder = token_decoder
        self.access_token_getter = access_token_getter

    def call_route(self, route: Callable, *args, **kwargs) -> any:
        access_token = self.access_token_getter()

        if not access_token:
            raise AccessTokenInvalidError("Access token is missing")

        try:
            self.token_decoder.decode(access_token)
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