from abc import ABC
from typing import Iterable

from flask_restful import Resource
from flask_middlewares import MiddlewareKeeper, Middleware

from config import DEFAULT_USER_SESSION_FACTORY, DEFAULT_ACCESS_TOKEN_FACTORY
from infrastructure.routers import FlaskJSONRequestAdditionalProxyController, GetterController
from services.account import AccountRegistrar
from services.repositories import UserRepository
from orm import db


class MiddlewareResource(MiddlewareKeeper, Resource, ABC):
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


class UserResource(Resource):
    get = FlaskJSONRequestAdditionalProxyController(GetterController(
        UserRepository(db),
        UserSchema(many=True, exclude=('password', 'password_hash'))
    ))
    post = FlaskJSONRequestAdditionalProxyController(CustomExternalController(
        AccountRegistrar(UserRepository(db)),
        UserSchema(many=True, exclude=('password', ))
    ))