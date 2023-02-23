from abc import ABC
from functools import cached_property, partial

from pyhandling import DelegatingProperty, execute_operation

from tools.formatters import format_dict


class ToolError(Exception):
    pass


class DecoratorError(ToolError):
    error = DelegatingProperty("_error")

    def __init__(self, error: Exception):
        self._error = error

    @cached_property
    def all_errors(self) -> tuple[Exception]:
        return partial(execute_operation, (self, ), '+')(
            self._error.deep_errors
            if isinstance(self._error, DecoratorError)
            else (self._error, )
        )

    def __str__(self) -> str:
        return f"{type(self).__name__} as {type(self._error).__name__}"


class ReportingError(DecoratorError):
    document = DelegatingProperty("_document")

    def __init__(self, error: Exception, document: dict):
        super().__init__(error)
        self._document = document

    def __str__(self) -> str:
        formatted_report = format_dict(self._document, line_between_key_and_value='=')

        return (
            super().__str__()
            + f" with {formatted_document}" if self._document else str()
        )


def convert_error_report_to_dict(
    report: ErrorReport,
    *,
    is_converting_error_message: bool = True,
    is_converting_error_detail: bool = True
) -> dict:
    result_dict = dict()

    if error.message and is_converting_error_message:
        result_dict['message'] = str(report.error)

    if error.document and is_converting_error_detail:
        result_dict['detail'] = report.document

    return result_dict


