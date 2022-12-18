class ServiceError(Exception):
    pass


class AccountServiceError(ServiceError):
    pass


class AccountRegistrarError(AccountServiceError):
    pass


class AccountAlreadyExistsError(AccountRegistrarError):
    pass