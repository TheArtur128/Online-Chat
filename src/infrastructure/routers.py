from abc import ABC, abstractmethod
from dataclasses import dataclass
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
    status_code: int
    metadata: dict


class IController(ABC):
    @abstractmethod
    def __call__(self, data: Iterable) -> ControllerResponse:
        pass


class ProxyController(IController):
    def __init__(self, controller: IController):
        self.controller = controller

    def __call__(self, data: Iterable) -> ControllerResponse:
        return self.controller(data)


class AdditionalDataProxyController(ProxyController, ABC):
    def __init__(self, controller: IController, *, is_data_showing_in_error: bool = False):
        super().__init__(controller)
        self.is_data_showing_in_error

    @property
    @abstractmethod
    def additional_data(self) -> Iterable:
        pass

    def __call__(self, data: Optional[Iterable] = None) -> ControllerResponse:
        return super().__call__(
            self.additional_data
            if data is None
            else self._get_combine_additional_data_with(data)
        )

    def _get_combine_additional_data_with(self, data: Iterable) -> Iterable:
        if (
            is_iterable_but_not_dict(data)
            and is_iterable_but_not_dict(self.additional_data)
        ):
            data = (*data, *self.additional_data)
        elif isinstance(data, dict) and isinstance(self.additional_data, dict):
            data = self.additional_data | data
        else:
            raise InputControllerDataCorrectionError(
                "Incompatible input data and additional data types",
                dict(
                    input_data_type=type(data).__name__,
                    additional_data_type=type(self.additional_data).__name__
                )
            )

        return data


class CustomAdditionalDataProxyController(AdditionalDataProxyController):
    def __init__(
        self, 
        controller: IController, 
        additional_data_resource: Callable[[], Iterable | dict] | Iterable | dict,
        *,
        is_data_showing_in_error: bool = False
    ):
        super().__init__(controller, is_data_showing_in_error)
        self.additional_data_resource = additional_data_resource

    @property
    def additional_data(self) -> Iterable | dict:
        return (
            self.additional_data_resource()
            if isinstance(self.additional_data_resource, Callable)
            else self.additional_data_resource
        )


class FlaskJSONRequestAdditionalProxyController(AdditionalDataProxyController):
    @property
    def additional_data(self) -> Iterable | dict:
        return request.json


class Controller(IController, ABC):
    def __call__(self, data: Iterable) -> ControllerResponse:
        response = self._handle_cleaned_data(self._get_cleaned_data_from(data))

        return response if isinstance(response, ControllerResponse) else ControllerResponse(response)

    @abstractmethod
    def _get_cleaned_data_from(self, data: Iterable) -> Iterable:
        pass

    @abstractmethod
    def _handle_cleaned_data(self, data: Iterable) -> ControllerResponse | object:
        pass


class SchemaController(Controller, ABC):
    _schema: Schema

    def _get_cleaned_data_from(self, data: Iterable) -> Iterable:
        error_reports = self._schema.validate(data)

        if error_reports:
            raise InputControllerDataCorrectionError(
                "Incorect input controller data",
                error_reports
            )

        return self._schema.dump(data)


class ServiceController(Controller, ABC):
    _service: Callable
    _is_service_input_multiple: bool = False

    def _handle_cleaned_data(self, data: Iterable) -> any:
        return (
            tuple(map(self._call_service_by, data))
            if self._is_service_input_multiple
            else self._call_service_by(data)
        )

    def _call_service_by(self, data: Iterable) -> any:
        return self._service(*data) if is_iterable_but_not_dict(data) else self._service(**data)


class ExternalController(ServiceController, SchemaController, ABC):
    def __init__(self, *, is_service_input_multiple: bool = False):
        self.is_service_input_multiple = is_service_input_multiple

    @property
    def is_service_input_multiple(self) -> bool:
        return self._is_service_input_multiple

    @is_service_input_multiple.setter
    def is_service_input_multiple(self, is_service_input_multiple: bool) -> None:
        self._is_service_input_multiple = self._schema.many = is_service_input_multiple


class CustomExternalController(ExternalController):
    service = DelegatingProperty('_service')
    schema = DelegatingProperty('_schema')

    def __init__(self, service: Callable, schema: Schema, *, is_service_input_multiple: bool = False):
        self.service = service
        self.schema = schema

        super().__init__(is_service_input_multiple=is_service_input_multiple)


class GetterController(SchemaController):
    schema = DelegatingProperty('_schema')

    def __init__(self, repository: IRepository, schema: Schema):
        self.schema = schema
        self.repository = repository

    def _handle_cleaned_data(self, data: Iterable[dict]) -> ControllerResponse:
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
