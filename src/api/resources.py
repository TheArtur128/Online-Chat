from abc import ABC
from functools import partial

from flask_restful import Resource
from pyhandling import then, positionally_unpack
from pyhandling.annotations import decorator

from frameworks.repositories import UserRepository
from frameworks.schemes import UserSchema, user_schema_without_password
from infrastructure.controllers import load_to, search_in
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

    get = (
        partial(load_to, user_schema_without_password(many=True))
        |then>> partial(positionally_unpack, partial(search_in, UserRepository(db)))
        |then>> partial(dict_value_map, user_schema_without_password().dump)
    )

    post = (
        partial(load_to, UserSchema(exclude=["password"]))
        |then>> partial(positionally_unpack, UserRepository(db).get_by)
        |then>> AccountRegistrar(UserRepository(db))
    )