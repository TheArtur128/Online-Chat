from flask_restful import Resource
from flask_middlewares import MiddlewareKeeper

from models import db
from config import DEFAULT_REFRESH_TOKEN_FACTORY, DEFAULT_ACCESS_TOKEN_FACTORY
from services.routers import UserDataGetterRouter, UserRegistrarRouter


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
    get = UserDataGetterRouter()
    post = UserRegistrarRouter(
        db,
        DEFAULT_REFRESH_TOKEN_FACTORY,
        DEFAULT_ACCESS_TOKEN_FACTORY
    )