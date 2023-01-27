from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

from marshmallow import Schema, ValidationError, fields
from flask_sqlalchemy import SQLAlchemy
from flask import request, make_response, Response, jsonify
from werkzeug.security import generate_password_hash

from infrastructure.errors import InputControllerDataCorrectionError
from services.repositories import IRepository
from tools.utils import is_iterable_but_not_dict, DelegatingProperty


controller = factory_for[ControllerResponse]


@dataclass(frozen=True)
class ControllerResponse:
    payload: any
    status_code: int = 200
    metadata: dict = field(default_factory=dict)


class SearchResult(TypedDict):
    found: Iterable = tuple()
    lost: Iterable = tuple()


def load_to(schema: Schema, chunk: Iterable) -> reformer_of[Iterable]:
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