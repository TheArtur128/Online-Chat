from typing import Optional, Callable

from flask_restful import Resource
from flask import request, Response
from marshmallow import Schema

from services.middlewares import ServiceErrorMiddleware
from schemes import FullUserSchema


class UserResource(Resource):
	user_serialization_schema: Schema = FullUserSchema(exclude=('password', 'password_hash'))
	user_deserialization_schema: Schema = FullUserSchema(exclude=('password', 'password_hash'))

	@ServiceErrorMiddleware().decorate
	def get(self):
		return self.user_deserialization_schema.dump(
			self.user_serialization_schema.load(request.json, many=True),
			many=True
		)
