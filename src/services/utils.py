from dataclasses import dataclass
from datetime import datetime

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

    return seconds_since_epoch if is_time_raw else datetime.fromtimestamp(timestamp)