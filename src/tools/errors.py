from abc import ABC
from functools import cached_property
from types import MappingProxyType
from typing import TypeVar, runtime_checkable, Protocol, Generic, Iterable, Self, Tuple

from pyhandling import open_collection_items, DelegatingProperty

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


def errors_from(error_storage: ErrorKepper | SingleErrorKepper | Exception) -> Tuple[Exception]:
    errors = (error_storage, ) if isinstance(error_storage, Exception) else tuple()

    if isinstance(error_storage, SingleErrorKepper):
        errors += errors_from(error_storage.error)
    if isinstance(error_storage, ErrorKepper):
        errors += open_collection_items(map(errors_from, error_storage.errors))

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


class ReportingError(ToolError):
    document = DelegatingProperty("_document")

    def __init__(self, error: Exception, document: dict):
        self.__error = error
        self.__document = MappingProxyType(document)

        super().__init__(self._error_message)

    @cached_property
    def _error_message(self) -> str:
        formatted_report = format_dict(self.__document, line_between_key_and_value='=')

        return (
            str(self.__error)
            + (" when {formatted_document}" if self.__document else str())
        )