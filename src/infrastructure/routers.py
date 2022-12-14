from abc import ABC, abstractmethod
from typing import Callable, Iterable, Optional

from marshmallow import Schema, ValidationError, fields
from flask_sqlalchemy import SQLAlchemy
from flask import request, make_response, Response, jsonify
from werkzeug.security import generate_password_hash

from infrastructure.services.repositories import IRepository
from infrastructure.errors import InputRouterDataCorrectionError
from tools.utils import is_iterable_but_not_dict


class IRouter(ABC):
    @abstractmethod
    def __call__(self, data: Iterable) -> any:
        pass


class ProxyRouter(IRouter):
    def __init__(self, router: IRouter):
        self.router = router

    def __call__(self, data: Iterable) -> any:
        return self.router(data)


class AdditionalDataProxyRouter(ProxyRouter, ABC):
    def __init__(self, router: IRouter, *, is_data_showing_in_error: bool = False):
        super().__init__(router)
        self.is_data_showing_in_error

    @property
    @abstractmethod
    def additional_data(self) -> Iterable:
        pass

    def __call__(self, data: Optional[Iterable] = None) -> any:
        return super().__call__(
            self.additional_data
            if data is None
            else self._get_combine_additional_data_with(data)
        )

    def _get_combine_additional_data_with(self, data: iterable) -> iterable:
        if (
            is_iterable_but_not_dict(data)
            and is_iterable_but_not_dict(self.additional_data)
        ):
            data = (*data, *self.additional_data)
        elif isinstance(data, dict) and isinstance(self.additional_data, dict):
            data = self.additional_data | data
        else:
            raise InputRouterDataCorrectionError(
                "Incompatible input data and additional data types",
                dict(
                    input_data_type=type(data).__name__,
                    additional_data_type=type(self.additional_data).__name__
                )
            )

        return data


class CustomAdditionalDataProxyRouter(AdditionalDataProxyRouter):
    def __init__(
        self, 
        router: IRouter, 
        additional_data_resource: Callable[[], Iterable | dict] | Iterable | dict,
        *,
        is_data_showing_in_error: bool = False
    ):
        super().__init__(router, is_data_showing_in_error)
        self.additional_data_resource = additional_data_resource

    @property
    def additional_data(self) -> Iterable | dict:
        return (
            self.additional_data_resource()
            if isinstance(self.additional_data_resource, Callable)
            else self.additional_data_resource
        )


class FlaskJSONRequestAdditionalProxyRouter(AdditionalDataProxyRouter):
    @property
    def additional_data(self) -> Iterable | dict:
        return request.json


class Router(IRouter, ABC):
    def __call__(self, data: Iterable) -> any:
        return self._handle_cleaned_data(self._get_cleaned_data_from(data))

    @abstractmethod
    def _get_cleaned_data_from(self, data: Iterable) -> Iterable:
        pass

    @abstractmethod
    def _handle_cleaned_data(self, data: Iterable) -> any:
        pass


class SchemaRouter(Router, ABC):
    _schema: Schema

    def _get_cleaned_data_from(self, data: Iterable) -> Iterable:
        error_reports = self._schema.validate(data)

        if error_reports:
            raise InputRouterDataCorrectionError(
                "Incorect input router data",
                error_reports
            )

        return self._schema.dump(data)


class ServiceRouter(Router, ABC):
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


class ExternalRouter(ServiceRouter, SchemaRouter):
    def __init__(self, *, is_service_input_multiple: bool = False):
        self.is_service_input_multiple = is_service_input_multiple

    @property
    def is_service_input_multiple(self) -> bool:
        return self._is_service_input_multiple

    @is_service_input_multiple.setter
    def is_service_input_multiple(self, is_service_input_multiple: bool) -> None:
        self._is_service_input_multiple = self._schema.many = is_service_input_multiple


class CustomExternalRouter(ExternalRouter):
    service = DelegatingProperty('_service')
    schema = DelegatingProperty('_schema')

    def __init__(self, service: Callable, schema: Schema, *, is_service_input_multiple: bool = False):
        self.service = service
        self.schema = schema

        super().__init__(is_service_input_multiple=is_service_input_multiple)


class GetterRouter(SchemaRouter):
    schema = DelegatingProperty('_schema')

    def __init__(self, repository: IRepository, schema: Schema):
        self.schema = schema
        self.repository = repository

    def _handle_cleaned_data(self, data: Iterable[dict]) -> list[dict]:
        received_data = list()
        non_existent_resource_data = list()

        for data_chunk in data:
            resource = self.repository.get_by(**data_chunk)
            
            if not user:
                raise UserDoesntExistError(
                    "User with data ({user_data}) does not exist".format(
                        user_data=format_dict(
                            user_data,
                            line_between_key_and_value='=',
                            value_changer=lambda value: f'"{value}"'
                        )
                    )
                )

            filtered_user_data.append(self._schema.dump(user, many=False))

        return filtered_user_data


class UserRegistrarRouter(DBRouter, SchemaRouter):
    _schema = FullUserSchema(many=False, exclude=('password_hash', ))

    def __init__(
        self,
        database: SQLAlchemy,
        user_session_factory: Callable[[], Token],
        user_access_token_factory: Callable[[User], str]
    ):
        super().__init__(database)

        self.user_session_factory = user_session_factory
        self.user_access_token_factory = user_access_token_factory

    def _handle_cleaned_data(self, data: dict) -> Response:
        if User.query.filter_by(url_token=data['url_token']).first():
            raise UserAlreadyExistsError(
                f"User with \"{data['url_token']}\" url token already exists"
            )

        user_session = self.user_session_factory()
        user = User(user_session=user_session, **data)

        self.database.session.add(user_session)
        self.database.session.add(user)

        return self._create_response_by(
            user_session.token,
            self.user_access_token_factory(user)
        )

    def _create_response_by(self, refresh_token: str, access_token: str) -> Response:
        response = make_response(
            jsonify({
                'refresh_token': refresh_token,
                'access_token': access_token
            }),
            201
        )

        response.set_cookie('refresh_token', refresh_token, httponly=True)
        response.set_cookie('access_token', access_token, httponly=True)

        return response
