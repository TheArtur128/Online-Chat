from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

from marshmallow import Schema, ValidationError, fields
from flask_sqlalchemy import SQLAlchemy
from flask_middlewares.standard.error_handling import ProxyErrorHandler, IErrorHandler
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


class HanlderErrorController(ProxyController):
    def __init__(
        self,
        controller: IController,
        error_handler_resource: Iterable[IErrorHandler] | IErrorHandler,
        *,
        proxy_error_handler_factory: Callable[[Iterable[IErrorHandler]], IErrorHandler] = ProxyErrorHandler
    ):
        super().__init__(controller)
        self.error_handler = (
            error_handler_resource
            if isinstance(error_handler_resource, IErrorHandler)
            else proxy_error_handler_factory(error_handler_resource)
        )

    def __call__(self, data: Iterable) -> ControllerResponse:
        try:
            return super().__call__(data)
        except Exception as error:
            return self.error_handler(error)


class AdditionalDataProxyController(ProxyController, ABC):
    def __init__(self, controller: IController, *, is_data_showing_in_error: bool = False):
        super().__init__(controller)
        self.is_data_showing_in_error = is_data_showing_in_error

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


class SchemaDataCleanerProxyController(ProxyController):
    def __init__(self, controller: IController, schema: Schema):
        super().__init__(controller)
        self.schema = schema

    def __call__(self, data: Iterable) -> ControllerResponse:
        error_reports = self._schema.validate(data)

        if error_reports:
            raise InputControllerDataCorrectionError(
                "Incorect input controller data",
                error_reports
            )

        return super().__call__(self._schema.dump(data))


class ServiceController(IController):
    def __init__(
        self,
        service: Callable,
        *,
        is_service_input_multiple: bool = False,
        response_factory: Callable[[any, int, dict], ControllerResponse] = ControllerResponse
    ):
        self.service = service
        self.is_service_input_multiple = is_service_input_multiple
        self.response_factory = response_factory

    def __call__(self, data: Iterable) -> ControllerResponse:
        return self.response_factory(
            tuple(map(self._call_service_by, data))
            if self._is_service_input_multiple
            else self._call_service_by(data)
        )

    def _call_service_by(self, data: Iterable) -> any:
        return self._service(*data) if is_iterable_but_not_dict(data) else self._service(**data)


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
