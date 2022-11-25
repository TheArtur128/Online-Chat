from typing import Optional, Callable

from flask_restful import Resource
from flask import request, Response
from marshmallow import Schema

from schemes import BaseUserSchema, FullUserSchema
from services.middlewares import ServiceErrorMiddleware


class UserResource(Resource):
	user_serialization_schema: Schema = BaseUserSchema(only=('user_url_token', ))
	user_deserialization_schema: Schema = FullUserSchema(exclude=('password', ))

	@ServiceErrorMiddleware().decorate
	def get(self):
		return self.user_deserialization_schema.dump(
			self.user_serialization_schema.load(request.json, many=True),
			many=True
		)
