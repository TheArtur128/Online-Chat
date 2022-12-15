from abc import ABC
from typing import Optional

from tools.errors import StatusCodeError, DocumentaryError


class InfrastructureError(Exception):
    pass


class AuthenticationError(StatusCodeError):
    status_code = 401


class AuthorizationError(StatusCodeError):
    status_code = 403


class RouterError(InfrastructureError):
    pass


class InputRouterDataCorrectionError(DocumentaryError, StatusCodeError, RouterError):
    status_code = 400


class ResorceError(RouterError):
    pass


class RouterResourceNotFoundError(DocumentaryError, StatusCodeError, ResorceError):
    status_code = 404


class UserAlreadyExistsError(StatusCodeError):
    status_code = 409


class AccessTokenInvalidError(AuthorizationError):
    pass