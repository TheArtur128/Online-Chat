from abc import ABC, abstractmethod
from typing import Callable, Iterable

from marshmallow import Schema, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask import request, make_response, Response, jsonify
from werkzeug.security import generate_password_hash

from models import User, Token
from services.middlewares import MiddlewareKeeper, DBSessionFinisherMiddleware
from services.schemes import FullUserSchema
from services.errors import UserDoesntExistError, UserAlreadyExistsError
from services.formatters import format_dict


class IRouter(ABC):
    @abstractmethod
    def __call__(self, data: dict | Iterable) -> any:
        pass


class Router(IRouter, ABC):
    def __call__(self) -> any:
        return self._handle_cleaned_data(self._get_cleaned_data_from(request.json))

    @abstractmethod
    def _get_cleaned_data_from(self, data: dict | Iterable) -> dict | Iterable:
        pass

    @abstractmethod
    def _handle_cleaned_data(self, data: dict | Iterable) -> any:
        pass


class MiddlewareRouter(MiddlewareKeeper, Router, ABC):
    def __call__(self) -> any:
        return self._proxy_middleware.call_route(super().__call__)


class SchemaRouter(Router, ABC):
    _schema: Schema

    def _get_cleaned_data_from(self, data: dict | Iterable) -> dict | Iterable:
        errors = self._schema.validate(data)

        if errors:
            raise ValidationError(errors)

        return self._schema.dump(data)


class UserDataGetterRouter(SchemaRouter):
    _schema = FullUserSchema(many=True, exclude=('password', 'password_hash'))

    def _handle_cleaned_data(self, data: Iterable[dict]) -> list[dict]:
        filtered_user_data = list()

        for user_data in data:
            user = User.query.filter_by(**user_data).first()
            
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


class DBRouter(MiddlewareRouter):
    _db_session_middleware_factory: Callable[[SQLAlchemy], DBSessionFinisherMiddleware] = DBSessionFinisherMiddleware

    _middleware_attribute_names = (
        *MiddlewareRouter._middleware_attribute_names,
        '_db_session_middleware'
    )

    def __init__(self, database: SQLAlchemy):
        self._db_session_middleware = self._db_session_middleware_factory(database)
        super().__init__()

    @property
    def database(self) -> SQLAlchemy:
        return self._db_session_middleware.database

    @database.setter
    def database(self, database: SQLAlchemy) -> None:
        self._db_session_middleware.database = database


class UserRegistrarRouter(DBRouter, SchemaRouter):
    _schema = FullUserSchema(many=False, exclude=('password_hash', ))

    def __init__(
        self,
        database: SQLAlchemy,
        user_refresh_token_factory: Callable[[], Token],
        user_access_token_factory: Callable[[User], str]
    ):
        super().__init__(database)

        self.user_refresh_token_factory = user_refresh_token_factory
        self.user_access_token_factory = user_access_token_factory

    def _get_cleaned_data_from(self, data: dict) -> dict:
        data = super()._get_cleaned_data_from(data)

        data['password_hash'] = generate_password_hash(data['password'])
        del data['password']

        data['name'] = data.get('name') or data.get('url_token')

        return data

    def _handle_cleaned_data(self, data: dict) -> Response:
        if User.query.filter_by(url_token=data['url_token']).first():
            raise UserAlreadyExistsError(
                f"User with \"{data['url_token']}\" url token already exists"
            )

        user_refresh_token = self.user_refresh_token_factory()
        user = User(refresh_token=user_refresh_token, **data)

        self.database.session.add(user_refresh_token)
        self.database.session.add(user)

        return self._create_response_by(
            user_refresh_token.body,
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
