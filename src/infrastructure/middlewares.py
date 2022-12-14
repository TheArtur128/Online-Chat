from typing import Callable

from flask import request
from flask_middlewares import Middleware
from flask_middlewares.standard.error_handling import JSONResponseErrorFormatter, TypeErrorHandler
from jwt import InvalidTokenError

from infrastructure.errors import AccessTokenInvalidError, DocumentaryError
from tools.jwt_serializers import IJWTDecoder
from tools.utils import get_status_code_from_error


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