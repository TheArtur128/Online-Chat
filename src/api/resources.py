from abc import ABC
from typing import Iterable, Callable

from flask_restful import Resource
from flask_middlewares import MiddlewareKeeper, Middleware

from frameworks.flask import FlaskJSONRequestAdditionalProxyController
from frameworks.repositories import UserRepository
from frameworks.schemes import UserSchema
from infrastructure.controllers import IController, SchemaDataCleanerProxyController, ServiceController, GetterController
from services.authorization import AccountRegistrar
from orm import db


class MiddlewareResourceMixin(MiddlewareKeeper, Resource, ABC):
    _internal_middlewares: Iterable[Middleware]

    def __init__(self, *args, **kwargs):
        super().__init__()

        for method_name in self.methods:
            method_name = method_name.lower()

            setattr(
                self,
                method_name,
                self._proxy_middleware.decorate(getattr(self, method_name))
            )

        super(Resource, self).__init__()


class ProxyControllerResourceMixin(Resource, ABC):
    _global_proxy_controller_factory: Callable[[Iterable[IController]], IController]

    def __init__(self, *args, **kwargs):
        for method_name in self.methods:
            method_name = method_name.lower()

            setattr(
                self,
                method_name,
                self._global_proxy_controller_factory((getattr(self, method_name), ))
            )

        super().__init__()


class UserResource(ProxyControllerResourceMixin):
    _global_proxy_controller_factory = FlaskJSONRequestAdditionalProxyController

    get = GetterController(
        UserRepository(db),
        UserSchema(many=True, exclude=('password', 'password_hash'))
    )

    post = SchemaDataCleanerProxyController(
        ServiceController(AccountRegistrar(UserRepository(db))),
        UserSchema(many=True, exclude=('password', ))
    )