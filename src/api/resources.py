from typing import Callable

from flask_restful import Resource
from flask import request, set_cookie

from services.middlewares import ServiceErrorMiddleware
from services.routers import UserDataGetterRouter, UserRegistrarRouter


class UserResource(Resource):
    user_data_getter: Callable[[dict], dict] = UserDataGetterRouter()
    user_registrar: Callable[[dict], any] = UserRegistrarRouter()

    @ServiceErrorMiddleware().decorate
    def get(self):
        return (
            self.user_data_getter(user_data)
            for user_data in request.json
        )

    @ServiceErrorMiddleware().decorate
    def post(self):
        refresh_token = self.user_registrar(request.json)
        
        set_cookie('refresh_token', refresh_token, httponly=True)

        return {'refresh_token': refresh_token}, 201
