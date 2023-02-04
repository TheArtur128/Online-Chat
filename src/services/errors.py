class ServiceError(Exception):
    pass


class RegistrationError(ServiceError):
    pass


class TokenError(ServiceError):
    pass


class AccessTokenError(TokenError):
    pass