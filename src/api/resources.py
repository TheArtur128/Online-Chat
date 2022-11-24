from typing import Optional, Callable

from flask_restful import Resource
from flask import request, Response
from marshmallow import Schema

from schemes import BaseUserSchema, FullUserSchema
from services.middlewares import ServiceErrorMiddleware


class UserResource(Resource):
	_user_serialization_schema: Schema = BaseUserSchema(only=('user_url_token', ))
	_user_deserialization_schema: Schema = FullUserSchema(exclude=('password', ))

	@ServiceErrorMiddleware().decorate
	def get(self):
		return self._user_deserialization_schema.dump(
			self._user_serialization_schema.load(request.json, many=True),
			many=True
		)
