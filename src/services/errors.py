from abc import ABC


class ServiceError(Exception):
    pass


class StatusCodeError(ServiceError, ABC):
    status_code: int


class AuthenticationError(StatusCodeError):
    status_code = 401


class ResorceServiceError(ServiceError):
    pass


class UserNotFoundError(ResorceServiceError, StatusCodeError):
    status_code = 404


class UserAlreadyExistsError(StatusCodeError):
    status_code = 409


class UserDoesntExistError(StatusCodeError):
    status_code = 404
