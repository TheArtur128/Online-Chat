from abc import ABC
from typing import Iterable, Callable

from flask_restful import Resource

from frameworks.flask import FlaskJSONRequestAdditionalProxyController
from frameworks.repositories import UserRepository
from frameworks.schemes import UserSchema
from services.authorization import AccountRegistrar
from orm import db


class DecoratedResourceMixin(Resource, ABC):
    _decorator: decorator

    def __init__(self, *args, **kwargs):
        for method_name in self.methods:
            method_name = method_name.lower()

            setattr(
                self,
                method_name,
                self._decorator(getattr(self, method_name))
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