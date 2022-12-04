from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from flask import Response
from marshmallow.validate import Length

from models import db


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


def get_status_code_from(response: any) -> int:
    if isinstance(response, Response):
        return response.status_code
    elif (
        isinstance(response, Iterable)
        and len(response) >= 2
        and isinstance(response[1], int | float)
        and int(response[1]) == response[1]
        and 400 <= response[1] <= 500
    ):
        return response[1]
    else:
        return 200