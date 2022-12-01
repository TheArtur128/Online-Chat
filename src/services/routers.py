from abc import ABC, abstractmethod
from typing import Callable
from secrets import token_hex

from marshmallow import Schema, ValidationError
from flask_sqlalchemy import SQLAlchemy

from models import db, User, Token
from services.abstractions.interfaces import IRouter
from services.factories import CustomMinuteTokenFactory, CustomArgumentFactory
from services.middlewares import MiddlewareKeeper, DBSessionFinisherMiddleware
from services.schemes import FullUserSchema


class Router(ABC):
    def __call__(self, data: dict) -> any:
        return self._handle_cleaned_data(self._get_cleaned_data_from(data))

    @abstractmethod
    def _get_cleaned_data_from(self, data: dict) -> dict:
        pass

    @abstractmethod
    def _handle_cleaned_data(self, data: dict) -> any:
        pass


class MiddlewareRouter(Router, MiddlewareKeeper, ABC):
    def __call__(self, data: dict) -> any:
        self._proxy_middleware.call_route(super().__call__, data)


class SchemaRouter(Router, ABC):
    _schema: Schema

    def _get_cleaned_data_from(self, data: dict) -> dict:
        errors = self._schema.validate(data)

        if errors:
            raise ValidationError(errors)

        return self._schema.dump(data)


class UserDataGetterRouter(SchemaRouter):
    _schema = FullUserSchema(many=False, exclude=('password', 'password_hash'))

    def _handle_cleaned_data(self, data: dict) -> dict:
        user = User.query.filter_by(**data).first()
        
        if not user:
            raise UserDoesntExistError(
                "User with data ({data}) does not exist".format(
                    user_data=format_dict(
                        data,
                        line_between_key_and_value='=',
                        value_changer=lambda value: f'"{value}"'
                    )
                )
            )

        return self._schema.dump(user)


class UserRegistrarRouter(MiddlewareRouter):
    _middleware_attribute_names = (*MiddlewareRouter._middleware_attribute_names, '_db_session_middleware')

    _db_session_middleware = DBSessionFinisherMiddleware(db)
    _schema = FullUserSchema(many=False, exclude=('password_hash', ))

    __user_refresh_token_factory: Callable[[], Token] = CustomMinuteTokenFactory(
        60*24*30,
        CustomArgumentFactory(token_hex, Token.body.comparator.type.length // 2)
    )

    @property
    def database(self) -> SQLAlchemy:
        return self._db_session_middleware.database

    @database.setter
    def database(self, database: SQLAlchemy) -> None:
        self._db_session_middleware.database = database

    def _get_cleaned_data_from(self, data: dict) -> dict:
        data = super()._get_cleaned_data_from(data)

        data['password_hash'] = generate_password_hash(data['password'])
        del data['password']

        return data

    def _handle_cleaned_data(self, data: dict) -> str:
        if User.query.filter_by(url_token=data['url_token']).first():
            raise UserAlreadyExistsError(
                f"User with \"{data['url_token']}\" url token already exists"
            )

        user_refresh_token = self.__user_token_factory()
        user = User(refresh_token=user_refresh_token, **data)

        self.database.session.add(user_refresh_token)
        self.database.session.add(user)

        return user_refresh_token.body