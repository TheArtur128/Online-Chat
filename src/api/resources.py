from abc import ABC
from typing import Iterable, Callable

from flask_restful import Resource

from frameworks.flask import FlaskJSONRequestAdditionalProxyController
from frameworks.repositories import UserRepository
from frameworks.schemes import UserSchema
from services.authorization import AccountRegistrar
from orm import db
from tools.utils import decorator_for_addition_data_by, dict_value_map


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


class UserResource(DecoratedResourceMixin):
    _decorator = decorator_for_addition_data_by(request.json)

    get = GetterController(
        UserRepository(db),
        UserSchema(many=True, exclude=('password', 'password_hash'))
    )

    post = SchemaDataCleanerProxyController(
        ServiceController(AccountRegistrar(UserRepository(db))),
        UserSchema(many=True, exclude=('password', ))
    )