from dataclasses import dataclass
from datetime import datetime
from typing import runtime_checkable, Protocol, Generator, Iterable, Callable, Tuple

from marshmallow.validate import Length
from pyannotating import Special
from pyhandling import on_condition, close, then, callmethod, mergely, take, return_, previous_action_decorator_of, next_action_decorator_of, getitem_of, by, documenting_by
from pyhandling.annotations import handler, reformer_of

from orm import db


@runtime_checkable
class StatusCodeKeeper(Protocol):
    status_code: int


def status_code_parsing_with_default(default_status_code: int) -> Callable[Special[StatusCodeKeeper], int]:
    return on_condition(
        isinstance |by| StatusCodeKeeper,
        getattr |by| "status_code",
        else_=take(default_status_code)
    )


def length_validator_by_column(column: str, model: db.Model) -> Length:
    return Length(max=getattr(model, column).comparator.type.length)


def ascii_range_as(range_: range) -> Generator[str, None, None]:
    return (chr(symbol_index) for symbol_index in range_)


def get_time_after(minutes: int, is_time_raw: bool = False) -> datetime | float:
    timestamp = datetime.today().timestamp() + minutes*60

    return timestamp if is_time_raw else datetime.fromtimestamp(timestamp)


def is_iterable_but_not_dict(data: any) -> bool:
    return isinstance(data, Iterable) and not isinstance(data, dict)


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


def merge(*funcs: Callable) -> Callable:
    def merged(*args, **kwargs) -> Tuple:
        return tuple(func(*args, **kwargs) for func in funcs)

    return merged


data_additing_decorator_by: Callable[[Callable[[], Iterable]], reformer_of[reformer_of[Iterable]]] = (
    mergely(take(mergely), take(close(combine_data_chunks)), second_chunk=return_)
    |then>> previous_action_decorator_of
)


merge_events: Callable[[...], Callable] = close(
    merge |then>> next_action_decorator_of(getitem_of |by| -1)
)


swap_keys_and_values: reformer_of[dict] = documenting_by(
    """Function to get dict with swaped keys and values."""
)(
    (callmethod |by| "items")
    |then>> close(map)(getitem_of |by| slice(1, 1, -1))
    |then>> dict
)