from typing import Callable, Iterable

from flask_restful import Resource
from flask import request

from models import db
from services.factories import DEFAULT_REFRESH_TOKEN_FACTORY, DEFAULT_ACCESS_TOKEN_FACTORY
from services.middlewares import MiddlewareKeeper, ServiceErrorMiddleware
from services.routers import UserDataGetterRouter, UserRegistrarRouter


class RoutResource(MiddlewareKeeper, Resource):
    _internal_middlewares = (ServiceErrorMiddleware(), )

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
