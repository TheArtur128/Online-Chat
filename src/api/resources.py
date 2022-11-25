from typing import Callable

from flask_restful import Resource
from flask import request
from marshmallow import Schema

from models import db
from schemes import FullUserSchema
from services.middlewares import ServiceErrorMiddleware
from services.authorization_services import DBUserRegistrar


class UserResource(Resource):
	user_schema: Schema = FullUserSchema(exclude=('password', 'password_hash'))
	user_registrar: Callable[[dict], any] = DBUserRegistrar(db)

	@ServiceErrorMiddleware().decorate
	def get(self):
		return self.user_schema.dump(
			self.user_schema.load(request.json, many=True),
			many=True
		)

	@ServiceErrorMiddleware().decorate
	def post(self):
		self.user_registrar(request.json)

		return dict(), 201
