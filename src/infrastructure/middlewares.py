from typing import Callable

from flask import request
from flask_middlewares import Middleware
from jwt import InvalidTokenError

from infrastructure.errors import AccessTokenInvalidError
from tools.jwt_serializers import IJWTDecoder


class AccessTokenRequiredMiddleware(Middleware):
    def __init__(self, jwt_decoder: IJWTDecoder):
        self.jwt_decoder = jwt_decoder

    def call_route(self, route: Callable, *args, **kwargs) -> any:
        access_token = request.cookies.get('access_token') or request.headers.get('access_token')

        if not access_token:
            raise AccessTokenInvalidError('Access token is missing')

        try:
            self.jwt_decoder.decode(access_token)
        except InvalidTokenError:
            raise AccessTokenInvalidError('Access token is invalid')

        return route(*args, **kwargs)
