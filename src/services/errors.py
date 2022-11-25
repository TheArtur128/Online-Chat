from abc import ABC


class SeviceError(Exception):
	pass


class StatusCodeError(SeviceError, ABC):
	status_code: int


class AuthenticationError(StatusCodeError):
	status_code = 401


class ResorceSeviceError(SeviceError):
	pass


class UserNotFoundError(ResorceSeviceError, StatusCodeError):
	status_code = 404


class UserAlreadyExistsError(StatusCodeError):
	status_code = 409


class UserDoesntExistError(StatusCodeError):
	status_code = 404
