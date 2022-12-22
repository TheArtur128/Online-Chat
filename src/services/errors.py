class ServiceError(Exception):
    pass


class AccountServiceError(ServiceError):
    pass


class AccountRegistrarError(AccountServiceError):
    pass


class AccountAlreadyExistsError(AccountRegistrarError):
    pass


class TokenError(ServiceError):
    pass


class MissingTokenError(TokenError):
    pass


class InvalidTokenError(TokenError):
    pass