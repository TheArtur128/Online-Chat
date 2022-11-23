from abc import ABC


class SeviceError(Exception):
	pass


class StatusCodeError(SeviceError, ABC):
	status_code: int


class AuthenticationError(StatusCodeError):
	status_code = 401
