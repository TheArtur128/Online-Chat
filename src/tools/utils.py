from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Self, Callable

from beautiful_repr import StylizedMixin, Field, TemplateFormatter
from flask import Response, request
from marshmallow.validate import Length

from orm import db


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


def get_time_after(minutes: int, is_time_raw: bool = False) -> datetime | float:
    timestamp = datetime.today().timestamp() + minutes*60

    return timestamp if is_time_raw else datetime.fromtimestamp(timestamp)


def get_status_code_from_error(error: Exception, *, default_error_code: int = 500) -> int:
    return StatusCodeError.status_code if isinstance(error, StatusCodeError) else default_error_code


def is_iterable_but_not_dict(data: any) -> bool:
    return isinstance(data, Iterable) and not isinstance(data, dict) 


def get_json_data_from_request() -> dict | Iterable:
    return request.json