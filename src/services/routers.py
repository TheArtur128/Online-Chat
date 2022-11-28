from abc import ABC, abstractmethod

from marshmallow import Schema, ValidationError

from models import db, User, Token
from services.middlewares import MiddlewareKeeper, DBSessionFinisherMiddleware
from services.schemes import FullUserSchema


class IRouter(ABC):
    @abstractmethod
    def __call__(self, data: dict) -> any:
        pass


class Router(IRouter, ABC):
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
