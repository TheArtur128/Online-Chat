from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from beautiful_repr import StylizedMixin, Field, TemplateFormatter
from marshmallow.validate import Length
from pyhandling import ActionChain, call, then, close
from pyhandling.annotations import decorator

from orm import db
from tools.errors import StatusCodeError


def create_length_validator_by_model_column(model: db.Model, column: str) -> Length:
    return Length(max=getattr(model, column).comparator.type.length)


@dataclass(frozen=True)
class ASCIIRange:
    start: int = 0
    end: int = 127
    step: int = 1

    def __post_init__(self):
        if self.step == 0:
            raise ValueError("step must not be zero")

    def __iter__(self) -> iter:
        return iter(
            (chr(symbol_index) for symbol_index in range(self.start, self.end, self.step))
        )


class DelegatingProperty:
    def __init__(self, delegated_attribute_name: str, *, settable: bool = True):
        self.delegated_attribute_name = delegated_attribute_name
        self.settable = settable

    def __get__(self, instance: object, owner: type) -> any:
        return getattr(instance, self.delegated_attribute_name)

    def __set__(self, instance: object, value: any) -> None:
        if not self.settable:
            raise AttributeError(
                "delegating property of '{attribute_name}' for '{class_name}' object is not settable".format(
                    attribute_name=self.delegated_attribute_name,
                    class_name=type(instance).__name__
                )
            )

        setattr(instance, self.delegated_attribute_name, value)


def get_time_after(minutes: int, is_time_raw: bool = False) -> datetime | float:
    timestamp = datetime.today().timestamp() + minutes*60

    return timestamp if is_time_raw else datetime.fromtimestamp(timestamp)


def get_status_code_from_error(error: Exception, *, default_error_code: int = 500) -> int:
    return (
        error.status_code
        if isinstance(error, StatusCodeError)
        else default_error_code
    )


def is_iterable_but_not_dict(data: any) -> bool:
    return isinstance(data, Iterable) and not isinstance(data, dict)


post_action_decorator: decorator = ActionChain(call).clone_with |then>> close
def dict_value_map(value_transformer: handler, dict_: dict) -> dict:
    return {
        _: value_transformer(value)
        for _, value in dict_.items()
    }


def combine_data_chunks(first_chunk: Iterable, second_chunk: Iterable) -> Iterable:
    if all(map(is_iterable_but_not_dict, (first_chunk, second_chunk))):
        return (*first_chunk, *second_chunk)
    elif isinstance(second_chunk, dict) and isinstance(first_chunk, dict):
        return first_chunk | second_chunk
    else:
        raise ReportingError(
            TypeError("Incompatible input chunks types"),
            dict(
                first_chunk_type=type(first_chunk).__name__,
                second_chunk_type=type(second_chunk).__name__
            )
        )


decorator_for_addition_data_by = (
    mergely(take(mergely), take(close(combine_data_chunks)), second_chunk=return_)
    |then>> previous_action_decorator_of
)