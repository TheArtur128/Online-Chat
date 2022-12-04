from abc import ABC, abstractmethod
from typing import Callable, Optional, Iterable, Self
from functools import wraps

from flask_sqlalchemy import SQLAlchemy
from flask import Response, abort, jsonify, request, redirect, url_for, Flask, Blueprint
from marshmallow import ValidationError
from jwt.exceptions import InvalidTokenError
from werkzeug.routing.exceptions import BuildError

from services.abstractions.interfaces import IJWTDecoder
from services.factories import CustomArgumentFactory
from services.errors import StatusCodeError, AccessTokenInvalidError, MiddlewareRegistrarConfigError
from services.utils import get_status_code_from, BinarySet


class Middleware(ABC):
    def decorate(self, route: Callable) -> Callable:
        @wraps(route)
        def body(*args, **kwargs) -> any:
            return self.call_route(route, *args, **kwargs)

        return body

    @abstractmethod
    def call_route(self, route: Callable, *args, **kwargs) -> any:
        pass


class ProxyMiddleware(Middleware):
    def __init__(self, middlewares: Iterable[Middleware]):
        self.middlewares = list(middlewares)

    def call_route(self, route: Callable, *args, **kwargs) -> any:
        call_layer = route

        for middleware in self.middlewares[::-1]:
            call_layer = CustomArgumentFactory(middleware.call_route, call_layer)

        return call_layer(*args, **kwargs)


class IMiddlewareAppRegistrar(ABC):
    @abstractmethod
    def init_app(
        self,
        app: Flask,
        *,
        for_view_names: Iterable[BinarySet | str] = BinarySet(),
        for_blueprints: Iterable[BinarySet | str | Blueprint] = BinarySet()
    ) -> None:
        pass


class MiddlewareAppRegistrar(IMiddlewareAppRegistrar):
    _proxy_middleware_factory: Callable[[Iterable[Middleware]], Middleware] = ProxyMiddleware
    _config_field_names: dict[str, str] = {
        'middlewares': 'MIDDLEWARES',
        'default_view_names': 'MIDDLEWARE_VIEW_NAMES',
        'default_blueprints': 'DEFAULT_BLUEPRINTS',
        'is_global_middlewares_higher': 'IS_GLOBAL_MIDDLEWARES_HIGHER',
        'is_blueprint_middlewares_higher': 'IS_BLUEPRINT_MIDDLEWARES_HIGHER',
        'blueprint_key': 'BLUEPRINT_MIDDLEWARES',
        'topics': {
            'default_middlewares': 'DEFAULT',
            'global_middlewares': 'GLOBAL'
        }
    }

    def __init__(
        self,
        middlewares: Iterable[Middleware],
        *,
        default_view_names: Optional[Iterable[str] | BinarySet] = None,
        default_blueprints: Optional[Iterable[str | Blueprint] | BinarySet] = None
    ):
        self.middleware = self._proxy_middleware_factory(middlewares)

        self.default_view_name_set = self.__get_set_from_raw_data(default_view_names)
        self.default_blueprint_set = self.__get_set_from_raw_data(default_blueprints)

    def init_app(
        self,
        app: Flask,
        *,
        for_view_names: Iterable[BinarySet | str] = BinarySet(),
        for_blueprints: Iterable[BinarySet | str | Blueprint] = BinarySet(),
    ) -> None:
        view_name_set = self.default_view_name_set & self.__get_set_from_raw_data(for_view_names)
        blueprint_set = self.default_blueprint_set & self.__get_set_from_raw_data(for_blueprints)

        blueprint_name_set = BinarySet(
            self.__get_blueprint_name_from(blueprint_set.including),
            self.__get_blueprint_name_from(blueprint_set.non_including)
        )

        for view_name, view_function in app.view_functions.items():
            if view_name in view_name_set and any(
                view_blueprint_name in blueprint_name_set
                for view_blueprint_name in view_name.split('.')[:-1]
            ):
                app.view_functions[view_name] = self.middleware.decorate(view_function)

    @classmethod
    def create_from_config(
        cls,
        config: dict,
        *args,
        topic: Optional[str] = None,
        default_view_names: Optional[Iterable[str] | BinarySet] = None,
        default_blueprints: Optional[Iterable[str | Blueprint] | BinarySet] = None,
        is_global_middlewares_higher: Optional[bool] = None,
        is_blueprint_middlewares_higher: Optional[bool] = None,
        for_blueprint: Optional[str] = None
        **kwargs,
    ) -> Self:
        global_middlewares = tuple()

        if for_blueprint is not None:
            global_middlewares = cls.__get_global_middlewares_from(config)
            config = config.get(cls._config_field_names['blueprint_key'], diec()).get(for_blueprint, dict())
       
        middlewares = config.get(cls._config_field_names['middlewares'])

        if middlewares is None:
            raise MiddlewareRegistrarConfigError(
                f"The config is missing the required field \"{cls._config_field_names['middlewares']}\""
            )

        if isinstance(middlewares, dict):
            middlewares = middlewares[topic or cls._config_field_names['topics']['default_middlewares']]

            additional_global_middlewares = cls.__get_global_middlewares_from(config)

            if (
                config.get(cls._config_field_names['is_blueprint_middlewares_higher'], True)
                if is_blueprint_middlewares_higher is None
                else is_blueprint_middlewares_higher
            ):
                global_middlewares = additional_global_middlewares + global_middlewares
            else:
                global_middlewares += additional_global_middlewares

        middleware_packs = [global_middlewares, middlewares]

        if not (
            config.get(cls._config_field_names['is_global_middlewares_higher'], True)
            if is_global_middlewares_higher is None
            else is_global_middlewares_higher
        ):
            middleware_packs.reverse()

        parsed_args = (*middleware_packs[0], *middleware_packs[1])

        if default_view_names is None:
            default_view_names = config.get(cls._config_field_names['default_view_names'])

        if default_blueprints is None:
            default_blueprints = config.get(cls._config_field_names['default_blueprints'])

        return cls(
            (*middleware_packs[0], *middleware_packs[1]),
            *args,
            default_view_names=default_view_names,
            default_blueprints=default_blueprints,
            **kwargs,
        )

    @staticmethod
    def __get_set_from_raw_data(raw_data: BinarySet | Iterable) -> BinarySet:
        return raw_data if isinstance(raw_data, BinarySet) else BinarySet(raw_data)

    @staticmethod
    def __get_blueprint_name_from(blueprints: None | Iterable[str | Blueprint]) -> tuple[str]:
        return tuple(
            blueprint if isinstance(blueprint, str) else blueprint.name
            for blueprint in blueprints
        ) if blueprints is not None else blueprints

    @staticmethod
    def __get_global_middlewares_from(
        middleware_config: dict[str, Iterable[Middleware]],
        topic: Optional[str] = None,
    ) -> tuple[Middleware]:
        return tuple(
            middleware_config.get([cls._config_field_names['topics']['global_middlewares']], tuple())
            if topic != cls._config_field_names['topics']['global_middlewares']
            else tuple()
        )


class MiddlewareKeeper(ABC):
    _middleware_attribute_names: Iterable[str] = ('_internal_middlewares', )
    _proxy_middleware_factory: Callable[[Iterable[Middleware]], ProxyMiddleware] = ProxyMiddleware

    _proxy_middleware: Optional[ProxyMiddleware]

    def __init__(self):
        self._update_middlewares()

    @property
    def _middlewares(self) -> Middleware:
        return tuple(self._proxy_middleware.middlewares)

    def _update_middlewares(self) -> None:
        self._proxy_middleware = self._proxy_middleware_factory(tuple(self.__parse_middlewares()))

    def __parse_middlewares(self) -> list[Middleware]:
        middlewares = list()

        for attribute_name in self._middleware_attribute_names:
            if not hasattr(self, attribute_name):
                continue

            attribute_value = getattr(self, attribute_name)

            if isinstance(attribute_value, Iterable):
                middlewares.extend(attribute_value)
            else:
                middlewares.append(attribute_value)

        return middlewares


class ServiceErrorFormatterMiddleware(Middleware):
    def call_route(self, route: Callable, *args, **kwargs) -> any:
        try:
            return route(*args, **kwargs)

        except StatusCodeError as error:
            status_code = error.status_code
            response = jsonify(
                error.messages
                if isinstance(error, ValidationError)
                else {'message': str(error)}
            )

        except ValidationError as error:
            status_code = 400
            response = jsonify(error.messages)

        response.status_code = status_code

        return response


class AbortBadStatusCodeMiddleware(Middleware):
    def call_route(self, route: Callable, *args, **kwargs) -> any:
        response = route(*args, **kwargs)

        status_code = get_status_code_from(response)

        if 400 <= status_code <= 500:
            abort(status_code)

        return response


class DBMiddleware(Middleware, ABC):
    def __init__(self, database: SQLAlchemy):
        self.database = database


class DBSessionFinisherMiddleware(DBMiddleware):
    def call_route(self, route: Callable, *args, **kwargs) -> any:
        try:
            result = route(*args, **kwargs)
            self.database.session.commit()

            return result

        except Exception as error:
            self.database.session.rollback()

            raise error


class AccessTokenRequiredMiddleware(Middleware):
    def __init__(self, jwt_decoder: IJWTDecoder):
        self.jwt_decoder = jwt_decoder

    def call_route(self, route: Callable, *args, **kwargs) -> any:
        access_token = request.cookies.get('access_token') or request.headers.get('access_token')

        if not access_token:
            raise AccessTokenInvalidError('Access token is missing')

        try:
            self.jwt_decoder.decode(access_token)
        except InvalidTokenError:
            raise AccessTokenInvalidError('Access token is invalid')

        return route(*args, **kwargs)


class StatusCodeRedirectorMiddleware(Middleware):
    def __init__(self, redirect_resource: str, status_codes: Iterable[int] | int):
        self.redirect_resource = redirect_resource
        self.status_codes = (
            tuple(status_codes)
            if isinstance(status_codes, Iterable)
            else (status_codes, )
        )

    @property
    def redirect_url(self) -> str:
        try:
            return url_for(self.redirect_resource)
        except BuildError:
            return self.redirect_resource

    def call_route(self, route: Callable, *args, **kwargs) -> any:
        response = route(*args, **kwargs)

        return (
            redirect(self.redirect_url)
            if get_status_code_from(response) in self.status_codes
            else response
        )