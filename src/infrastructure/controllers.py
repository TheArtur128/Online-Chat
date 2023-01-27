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


@dataclass(frozen=True)
class ControllerResponse:
    payload: any
    status_code: int = 200
    metadata: dict = field(default_factory=dict)


class IController(ABC):
    @abstractmethod
    def __call__(self, data: Iterable) -> ControllerResponse:
        pass


class ProxyController(IController):
    def __init__(self, controller: IController):
        self.controller = controller

    def __call__(self, data: Iterable) -> ControllerResponse:
        return self.controller(data)


            )
        )


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

class GetterController(IController):
    def __init__(self, repository: IRepository, schema: Schema):
        self.repository = repository
        self.schema = schema

    def __call__(self, data: Iterable) -> ControllerResponse:
        received_data = list()
        non_existent_resource_data = list()

        for data_chunk in data:
            resource = self.repository.get_by(**data_chunk)
            
            (received_data if resource is not None else non_existent_resource_data).append(
                self.schema.dump(resource, many=False)
            )

        return ControllerResponse(
            status_code=(404 if non_existent_resource_data else 200),
            payload={
                'received': received_data,
                'lost': non_existent_resource_data
            }
        )
