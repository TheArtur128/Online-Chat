from typing import Callable

from flask_restful import Resource
from flask import request
from marshmallow import Schema

from services.middlewares import ServiceErrorMiddleware
from schemes import FullUserSchema


class UserResource(Resource):
	user_schema: Schema = FullUserSchema(exclude=('password', 'password_hash'))

	@ServiceErrorMiddleware().decorate
	def get(self):
		return self.user_schema.dump(
			self.user_schema.load(request.json, many=True),
			many=True
		)
