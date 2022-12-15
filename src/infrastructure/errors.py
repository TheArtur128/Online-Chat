from abc import ABC
from typing import Optional


class InfrastructureError(Exception):
    pass


class DocumentaryError(InfrastructureError):
    def __init__(self, message_template: str = str(), document: Optional[dict] = None):
        self.message_template = message_template
        self.document = document

    @property
    def message(self) -> str:
        return (
            self.message_template.format(document=str(self.document))
            if self.document is not None and '{document}' in self.message_template
            else self.message_template
        )

    def __str__(self) -> str:
        return (
            str(self.document)
            if not self.message_template and self.document is not None
            else self.message
        )


class StatusCodeError(InfrastructureError, ABC):
    status_code: int


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