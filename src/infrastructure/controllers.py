from dataclasses import dataclass, field
from functools import partial
from typing import Callable, Iterable, TypedDict

from marshmallow import Schema
from pyhandling import then, on_condition, raise_, ArgumentPack
from pyhandling.annotations import reformer_of

from services.repositories import IRepository
from tools.errors import ReportingError
from tools.utils import is_iterable_but_not_dict


class SearchResult(TypedDict):
    found: Iterable = tuple()
    lost: Iterable = tuple()


def convert_by(schema: Schema, chunk: Iterable) -> Iterable:
    return chunk >= (
        returnly(
            schema.validate
            |then>> partial(on_condition, bool)(
                partial(ReportingError, ValueError("Incorect input data"))
                |then>> raise_
            )
        )
        |then>> schema.dump
    )


def call_service(service: Callable, chunk: Iterable) -> Any:
    return service(*data) if is_iterable_but_not_dict(data) else service(**data)


def search_in(repository: IRepository, query_packs: Iterable[ArgumentPack]) -> Iterable:
    found_data = list()
    lost_data = list()

    for query_pack in query_packs:
        resource = query_pack.call(self._repository.get_by)
        
        (found_data if resource is not None else lost_data).append(resource)

    return SearchResult(found=tuple(found_data), lost=tuple(lost_data))