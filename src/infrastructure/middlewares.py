from typing import Callable, Optional

from flask import request
from flask_middlewares import Middleware
from flask_middlewares.standard.error_handling import JSONResponseErrorFormatter, TypeErrorHandler
from jwt import InvalidTokenError

from infrastructure.errors import AccessTokenInvalidError, DocumentaryError
from tools.jwt_serializers import IJWTDecoder
from tools.utils import get_status_code_from_error


class AccessTokenRequiredMiddleware(Middleware):
    def __init__(self, jwt_decoder: IJWTDecoder, access_token_getter: Callable[[], Optional[str]]):
        self.jwt_decoder = jwt_decoder
        self.access_token_getter = access_token_getter

    def call_route(self, route: Callable, *args, **kwargs) -> any:
        access_token = self.access_token_getter()

        if not access_token:
            raise AccessTokenInvalidError("Access token is missing")

        try:
            self.jwt_decoder.decode(access_token)
        except InvalidTokenError:
            raise AccessTokenInvalidError("Access token is invalid")

        return route(*args, **kwargs)


class DocumentaryErrorJSONResponseFormatter(JSONResponseErrorFormatter, TypeErrorHandler):
    _correct_error_types_to_handle = (DocumentaryError, )
    _get_status_code_from = staticmethod(get_status_code_from_error)

    def _get_response_body_from(self, error: DocumentaryError) -> dict:
        response_body = {'error-type': type(error).__name__}

        if error.message:
            response_body['message'] = error.message

        if error.document:
            response_body['detail'] = error.document

        return response_body


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

