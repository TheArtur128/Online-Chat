from abc import ABC
from typing import Optional

from tools.errors import StatusCodeError, DocumentaryError


class InfrastructureError(Exception):
    pass


class ControllerError(InfrastructureError):
    pass


class InputControllerDataCorrectionError(DocumentaryError, StatusCodeError, ControllerError):
    status_code = 400


class ResorceError(ControllerError):
    pass


class ControllerResourceNotFoundError(DocumentaryError, StatusCodeError, ResorceError):
    status_code = 404


class UserAlreadyExistsError(StatusCodeError, ResorceError):
    status_code = 409


class AccessTokenInvalidError(StatusCodeError):
    status_code = 403