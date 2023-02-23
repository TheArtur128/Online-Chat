from abc import ABC
from functools import cached_property, partial

from pyhandling import DelegatingProperty, execute_operation

from tools.formatters import format_dict


class ToolError(Exception):
    pass


StoredErrorT = TypeVar("StoredErrorT", bound=Exception)


@runtime_checkable
class SingleErrorKepper(Protocol, Generic[StoredErrorT]):
    error: StoredErrorT


@runtime_checkable
class ErrorKepper(Protocol, Generic[StoredErrorT]):
    errors: Iterable[Self | SingleErrorKepper[StoredErrorT] | StoredErrorT]

class ReportingError(DecoratorError):
    document = DelegatingProperty("_document")

    def __init__(self, error: Exception, document: dict):
        super().__init__(error)
        self._document = document
def errors_from(error_storage: ErrorKepper | SingleErrorKepper | Exception) -> Tuple[Exception]:
    errors = (error_storage, ) if isinstance(error_storage, Exception) else tuple()

    def __str__(self) -> str:
        formatted_report = format_dict(self._document, line_between_key_and_value='=')
    if isinstance(error_storage, SingleErrorKepper):
        errors += errors_from(error_storage.error)
    if isinstance(error_storage, ErrorKepper):
        errors += open_collection_items(map(errors_from, error_storage.errors))

        return (
            super().__str__()
            + f" with {formatted_document}" if self._document else str()
        )
    return errors


@runtime_checkable
class ErrorReport(Protocol, Generic[StoredErrorT]):
    error: StoredErrorT
    document: MappingProxyType


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


