from abc import ABC


class InfrastructureError(Exception):
    pass


class RouterError(InfrastructureError):
    pass


class InputRouterDataCorrectionError(RouterError):
    pass


class StatusCodeError(InfrastructureError, ABC):
    status_code: int


class AuthenticationError(StatusCodeError):
    status_code = 403


class AuthorizationError(StatusCodeError):
    status_code = 401


class ResorceError(InfrastructureError):
    pass


class UserNotFoundError(ResorceError, StatusCodeError):
    status_code = 404


class UserAlreadyExistsError(StatusCodeError):
    status_code = 409


class AccessTokenInvalidError(AuthorizationError):
    pass