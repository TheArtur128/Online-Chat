from typing import Callable

from flask_middlewares.standard.error_handling import IErrorHandler, JSONResponseErrorFormatter, TypeErrorHandler

from tools.errors import DocumentaryError
from tools.utils import get_status_code_from_error


class DocumentaryErrorJSONResponseFormatter(JSONResponseErrorFormatter, TypeErrorHandler):
    _correct_error_types_to_handle = (DocumentaryError, )
    _get_status_code_from = staticmethod(get_status_code_from_error)

    def _get_response_body_from(self, error: DocumentaryError) -> dict:
        response_body = {'error-type': type(error).__name__}

        if error.message:
            response_body['message'] = error.message

        if error.document:
            response_body['detail'] = error.document

        return response_body


class ReplacementErrorRaiser(IErrorHandler):
    def __init__(
        self,
        error_factory_by_error_type: dict[type, Callable[[str], Exception]] = dict(),
        **keyword_error_factory_by_error_type: Callable[[str], Exception]
    ):
        keyword_error_factory_by_error_type = {
            globals()[factory_name]: _
            for factory_name, _ in keyword_error_factory_by_error_type.items()
        }

        self.error_factory_by_error_type = (
            error_factory_by_error_type
            | keyword_error_factory_by_error_type
        )

    def __call__(self, error: Exception) -> any:
        for error_type, error_factory in self.error_factory_by_error_type.items():
            if isinstance(error, error_type):
                raise error_factory(str(error))
